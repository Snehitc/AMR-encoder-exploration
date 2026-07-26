import argparse
import pprint

from tqdm import tqdm, trange
import numpy as np
import os
from collections import OrderedDict, defaultdict
from easydict import EasyDict

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from basic_utils import AverageMeter
from span_utils import span_cxw_to_xx

from config import BaseOptions

import torch
import torch.nn.functional as F
import torch.backends.cudnn as cudnn
from torch.utils.data import DataLoader

from dataset import StartEndDataset, start_end_collate, prepare_batch_inputs
from postprocessing import PostProcessorDETR
from standalone_eval.eval import eval_submission

from basic_utils import save_jsonl, save_json
from qd_detr import build_model as build_model_qd_detr

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s.%(msecs)03d:%(levelname)s:%(name)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.INFO)



def wbf_1d(predictions, iou_thr=0.70):
    """
    Weighted Boxes Fusion for 1D temporal boundaries.
    Mathematically fuses overlapping predictions to tighten boundaries.
    predictions: list of [st, ed, score]
    """
    if not predictions:
        return []
    
    # Sort by confidence descending
    predictions = sorted(predictions, key=lambda x: x[2], reverse=True)
    fused_boxes = []
    
    for box in predictions:
        st, ed, score = box[0], box[1], box[2]
        best_iou, best_idx = 0.0, -1
        
        # Find best overlapping box cluster
        for idx, f_box in enumerate(fused_boxes):
            f_st, f_ed, f_max_score, weight_sum = f_box
            inter = max(0, min(ed, f_ed) - max(st, f_st))
            union = (ed - st) + (f_ed - f_st) - inter
            iou = inter / (union + 1e-6)
            if iou > iou_thr and iou > best_iou:
                best_iou, best_idx = iou, idx
                
        if best_idx != -1:
            # Fuse the coordinates based on confidence weights
            f_st, f_ed, f_max_score, weight_sum = fused_boxes[best_idx]
            new_weight = weight_sum + score
            new_st = (f_st * weight_sum + st * score) / new_weight
            new_ed = (f_ed * weight_sum + ed * score) / new_weight
            # Keep max score of the cluster for prediction confidence
            fused_boxes[best_idx] = [new_st, new_ed, max(f_max_score, score), new_weight] 
        else:
            fused_boxes.append([st, ed, score, score])
            
    return [[float(f"{b[0]:.4f}"), float(f"{b[1]:.4f}"), float(f"{b[2]:.4f}")] for b in fused_boxes]

def eval_epoch_post_processing(submission, opt, gt_data, save_submission_filename):
    logger.info("Saving/Evaluating before nms results")
    submission_path = os.path.join(opt.results_dir, opt.feat_model_combination, save_submission_filename)
    save_jsonl(submission, submission_path)

    if opt.eval_split_name in ["val", "test"]:
        metrics = eval_submission(submission, gt_data)
        save_metrics_path = submission_path.replace(".jsonl", "_metrics.json")
        save_json(metrics, save_metrics_path, save_pretty=True, sort_keys=False)
        latest_file_paths = [submission_path, save_metrics_path]
    else:
        metrics = None
        latest_file_paths = [submission_path, ]

    return metrics, latest_file_paths


@torch.no_grad()
def compute_mr_results(model, eval_loader, opt, criterion=None):
    batch_input_fn = cg_detr_prepare_batch_inputs if opt.model_name == 'cg_detr' else prepare_batch_inputs
    loss_meters = defaultdict(AverageMeter)

    mr_res = []
    for batch in tqdm(eval_loader, desc="compute st ed scores"):
        query_meta = batch[0]
        model_inputs, targets = batch_input_fn(batch[1], opt.device)
        outputs = model(**model_inputs)

        # compose predictions
        pred_spans = outputs["pred_spans"].cpu()  # (bsz, #queries, 2)
        prob = F.softmax(outputs["pred_logits"], -1)  # (batch_size, #queries, #classes=2)
        scores = prob[..., 0].cpu()  # * (batch_size, #queries)  foreground label is 0, we directly take it

        # Hamza: --- IOU RE-RANKING ---
        if "pred_iou" in outputs:
            pred_iou = outputs["pred_iou"].cpu().squeeze(-1)
            alpha = 1.5  # Soft calibration multiplier tuning parameter
            scores = scores * (pred_iou ** alpha)
        # ---------------------------

        for idx, (meta, spans, score) in enumerate(zip(query_meta, pred_spans, scores)):            
            spans = span_cxw_to_xx(spans) * meta["duration"]
            cur_ranked_preds = torch.cat([spans, score[:, None]], dim=1).tolist()
            cur_ranked_preds = sorted(cur_ranked_preds, key=lambda x: x[2], reverse=True)     # Hamza: Commented
            cur_ranked_preds = [[float(f"{e:.4f}") for e in row] for row in cur_ranked_preds] # Hamza: Commented

            # Hamza: Fuse overlapping boxes to tighten the final temporal boundary
            #cur_ranked_preds = wbf_1d(cur_ranked_preds, iou_thr=0.55)

            cur_query_pred = dict(
                qid=meta["qid"],
                query=meta["query"],
                vid=meta["vid"],
                pred_relevant_windows=cur_ranked_preds,
            )

            mr_res.append(cur_query_pred)

        if criterion:
            loss_dict = criterion(outputs, targets)
            weight_dict = criterion.weight_dict
            losses = sum(loss_dict[k] * weight_dict[k] for k in loss_dict.keys() if k in weight_dict)
            loss_dict["loss_overall"] = float(losses)
            for k, v in loss_dict.items():
                loss_meters[k].update(float(v) * weight_dict[k] if k in weight_dict else float(v))

    post_processor = PostProcessorDETR(
        clip_length=opt.clip_length, min_ts_val=0, max_ts_val=300,
        min_w_l=1, max_w_l=300, move_window_method="left",
        process_func_names=("clip_ts", "round_multiple")
    )

    mr_res = post_processor(mr_res)
    return mr_res, loss_meters


def get_eval_res(model, eval_loader, opt, criterion):
    """compute and save query and video proposal embeddings"""
    eval_res, eval_loss_meters = compute_mr_results(model, eval_loader, opt, criterion)
    return eval_res, eval_loss_meters


def eval_epoch(model, eval_dataset, opt, save_submission_filename, criterion):
    logger.info("Generate submissions")
    model.eval()
    criterion.eval()

    eval_loader = DataLoader(
        eval_dataset,
        collate_fn=start_end_collate,
        batch_size=opt.eval_bsz,
        num_workers=opt.num_workers,
        shuffle=False,
    )

    submission, eval_loss_meters = get_eval_res(model, eval_loader, opt, criterion)        
    metrics, latest_file_paths = eval_epoch_post_processing(
        submission, opt, eval_dataset.data, save_submission_filename)
    return metrics, eval_loss_meters, latest_file_paths


def setup_model(opt):
    print(opt.feature_model_text)
    """setup model/optimizer/scheduler and load checkpoints when needed"""
    logger.info("setup model/optimizer/scheduler")
    model, criterion = build_model_qd_detr(opt)

    if opt.device == "cuda":
        logger.info("CUDA enabled.")
        model.to(opt.device)
        criterion.to(opt.device)

    param_dicts = [{"params": [p for n, p in model.named_parameters() if p.requires_grad]}]
    optimizer = torch.optim.AdamW(param_dicts, lr=opt.lr, weight_decay=opt.wd)
    lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, opt.lr_drop)

    return model, criterion, optimizer, lr_scheduler


def start_inference(opt):
    logger.info("Setup config, data and model...")

    # dataset & data loader
    dataset_config = EasyDict(
        data_path=opt.val_path if opt.eval_split_name == 'val' else opt.test_path,
        ctx_mode=opt[opt.feature_model_audio[0]].ctx_mode,
        a_feat_dir=[opt[_feature_model_audio].a_feat_dir for _feature_model_audio in opt.feature_model_audio],
        q_feat_dir=[opt[_feature_model_text].t_feat_dir for _feature_model_text in opt.feature_model_text],
        q_feat_type="last_hidden_state",
        a_feat_type=opt[opt.feature_model_audio[0]].a_feat_type,
        max_q_l=opt.max_q_l,
        max_a_l=opt.max_a_l,
        clip_len=opt.clip_length,
        max_windows=opt.max_windows,
        span_loss_type=opt.span_loss_type,
        load_labels=True,
    )

    eval_dataset = StartEndDataset(**dataset_config)
    model, criterion, _, _ = setup_model(opt)
    checkpoint = torch.load(opt.model_path, weights_only=False)
    model.load_state_dict(checkpoint["model"])
    logger.info("Model checkpoint: {}".format(opt.model_path))

    logger.info("Starting inference...")
    save_submission_filename = "submission.jsonl"

    with torch.no_grad():
        metrics, eval_loss_meters, latest_file_paths = \
            eval_epoch(model, eval_dataset, opt, save_submission_filename, criterion)
    logger.info("metrics_no_nms {}".format(pprint.pformat(metrics["brief"], indent=4)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', type=str, required=True, help='config path')
    parser.add_argument('--model_path', '-m', type=str, required=True, help='model checkpoint path')
    parser.add_argument('--split', '-s', type=str, default='val', choices=['val', 'test'], help='split name: val or test')

    parser.add_argument('--feature_model_audio', nargs='+', type=str, required=True, help='[MSCLAP, M2D, LAION, OpenFLAM, WavLM, BEATs]')
    parser.add_argument('--feature_model_text', nargs='+', type=str, required=True, help='[MSCLAP, M2D, LAION, OpenFLAM, RoBERTa, T5]')
    
    args = parser.parse_args()
    
    option_manager = BaseOptions(args)
    option_manager.parse()
    opt = option_manager.option

    opt.model_path = args.model_path
    opt.eval_split_name = args.split
    start_inference(opt)
