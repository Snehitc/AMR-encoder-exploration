# dcase2026_task6_baseline
[QD-DETR](https://github.com/wjun0830/QD-DETR)-based baseline for DCASE 2026 challenge task 6.

## Model architecture
TBD

## Getting started
0. Clone this repository
```
git clone https://github.com/awkrail/dcase2026_task6_baseline.git
```
1. Install Pytorch & depndency libraries
Install pytorch, torchvision, and torchaudio based on your GPU environments. Note that the inference API is available for CPU environments. We tested the codes on Python 3.9 and CUDA 11.8:
```
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```
2. Prepare feature files
Download [CASTELLA dataset](https://zenodo.org/records/17412176) and [Clotho-Moment dataset](https://zenodo.org/records/17129257).
```
wget https://zenodo.org/records/17412176/files/features.tar.gz
tar -zxvf features.tar.gz
```

```
wget https://zenodo.org/api/records/17129257/files-archive
clotho-moment_features.tar.part-* > clotho-moment_features.tar
tar -xvf clotho-moment_features.tar
```

These feature files are also available in HuggingFace.
- [CASTELLA dataset](https://huggingface.co/datasets/lighthouse-emnlp2024/CASTELLA_CLAP_features)
- [Clotho-Moment dataset](https://huggingface.co/datasets/lighthouse-emnlp2024/Clotho-Moment_CLAP_features)


## Training and evaluation
0. Train a model
```
python src/train.py --config config.yml  
```
- `config.yml` is for CASTELLA. If you train models on Clotho-Moment, use `config-pretraining.yml`
- If you use pre-trained model weights, use `--resume ./**/{checkpoint}.pth`

1. Evaluation
Reproduce the evaluation on the `val` set.
```
python src/evaluate.py --config config.yml --model_path results/best_checkpoint.pth
```
The result is:
```
2026-02-28 21:24:35.081:INFO:__main__ - Setup config, data and model...
2026-02-28 21:24:35.088:INFO:__main__ - setup model/optimizer/scheduler
2026-02-28 21:24:35.741:INFO:__main__ - CUDA enabled.
2026-02-28 21:24:36.326:INFO:__main__ - Model checkpoint: results/best_checkpoint.pth
2026-02-28 21:24:36.326:INFO:__main__ - Starting inference...
2026-02-28 21:24:36.326:INFO:__main__ - Generate submissions
compute st ed scores: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 4/4 [00:02<00:00,  1.72it/s]
convert to multiples of clip_length=1: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 352/352 [00:00<00:00, 30208.19it/s]
2026-02-28 21:24:38.670:INFO:__main__ - Saving/Evaluating before nms results
full: [0, 1500], 352/352=100.00 examples.
[eval_moment_retrieval] [full] 0.10 seconds
2026-02-28 21:24:38.776:INFO:__main__ - metrics_no_nms OrderedDict([   ('MR-full-R1@0.5', 26.14),
                ('MR-full-R1@0.7', 14.2),
                ('MR-full-mAP', 11.69),
                ('MR-full-mAP@0.5', 23.42),
                ('MR-full-mAP@0.75', 9.58)])
```

Reproduce the evaluation on the `test` set:
```
python src/evaluate.py --config config.yml --split test --model_path results/best_checkpoint.pth
```
The result is:
```
2026-02-28 21:25:10.009:INFO:__main__ - Setup config, data and model...
2026-02-28 21:25:10.019:INFO:__main__ - setup model/optimizer/scheduler
2026-02-28 21:25:10.654:INFO:__main__ - CUDA enabled.
2026-02-28 21:25:11.240:INFO:__main__ - Model checkpoint: results/best_checkpoint.pth
2026-02-28 21:25:11.240:INFO:__main__ - Starting inference...
2026-02-28 21:25:11.240:INFO:__main__ - Generate submissions
compute st ed scores: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 14/14 [00:07<00:00,  1.83it/s]
convert to multiples of clip_length=1: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1347/1347 [00:00<00:00, 31431.38it/s]
2026-02-28 21:25:18.938:INFO:__main__ - Saving/Evaluating before nms results
full: [0, 1500], 1347/1347=100.00 examples.
[eval_moment_retrieval] [full] 0.28 seconds
2026-02-28 21:25:19.230:INFO:__main__ - metrics_no_nms OrderedDict([   ('MR-full-R1@0.5', 23.09),
                ('MR-full-R1@0.7', 10.47),
                ('MR-full-mAP', 8.99),
                ('MR-full-mAP@0.5', 20.14),
                ('MR-full-mAP@0.75', 7.49)])
```

## Preparation for submission.json
Run the following command to create submission file.
```
python src/create_submission.py --config config.yml --model_path results/best_checkpoint.pth
```
You can get `private_submission.jsonl` file under `results` directory. For details, please read [this README.md](src/standalone_eval/README.md)

## Citation
If you find this code useful for your research, please cite the original paper:
```
@inproceedings{munakata2025audiomoment,
  author = {Munakata, Hokuto and Nishimura, Taichi and Nakada, Shota and Komatsu, Tatsuya},
  title = {Language-based Audio Moment Retrieval},
  booktitle = {Proc. ICASSP},
  year = {2025},
  pages = {1-5},
  _pdf = {https://arxiv.org/pdf/2409.15672}
}
```
QD-DETR citation:
```
@inproceedings{qddetr
    author = {WonJun Moon and Sangeek Hyun and SangUk Park and Dongchan Park and Jae-Pil Heo},
    title = {Query-Dependent Video Representation for Moment Retrieval and Highlight Detection},
    booktitle = {Proc. CVPR},
    year = {2023},
}
```

## Others
This code is based on [lighthouse](https://github.com/line/lighthouse).


## Contact
taichitary@gmail.com
hokuto.munakata@lycorp.co.jp
