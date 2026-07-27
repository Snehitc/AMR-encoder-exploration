# 🚧 Under Construction 🚧

- This repo is forked from the baseline of DCASE task 6, and I'll modify part of the code in this repository to replicate my experiments as our submission to the challenge.
- Please wait for modifications before using it.
- The `Under Construction` tag will be removed once updates are completed.

# --- Work in progress ---

# Pipeline
[Figure of Pipeline]

# Setup
## 1. Clone this repository
```
git clone --depth 1 https://github.com/Snehitc/AMR-encoder-exploration.git && rm -rf AMR-encoder-exploration/.git
cd AMR-encoder-exploration
```
## 2. Create Environment
```
conda create -n AMR python=3.12
conda activate AMR
```
## 3. Install PyTorch (CUDA Version)
```
pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124
```
## 4. Install Requirements
```
pip install -r requirements.txt
```

# Dataset - _Extracted Features_
| Dataset | Link |
| :-: | :-: |
| CASTELLA | [CASTELLA dataset](https://zenodo.org/records/20772071) |
| Clotho-Moment | [Clotho-Moment dataset](https://zenodo.org/records/20770460) |


# Usage
## Training
Non-Ensemble
> ```
> python src/train.py --config config_pretraining.yml \
> --feature_model_audio M2D --feature_model_text M2D
> ```

> ```
> python src/train.py --config config.yml \
> --feature_model_audio M2D --feature_model_text M2D \
> --resume results_pretraining/A-M2D_T-M2D/best_checkpoint.pth
> ```

Ensemble
> ```
> python src/train.py --config config_pretraining.yml \
> --feature_model_audio M2D LAION --feature_model_text M2D LAION
> ```

> ```
> python src/train.py --config config.yml \
> --feature_model_audio M2D LAION --feature_model_text M2D LAION \
> --resume results_pretraining/A-M2D_LAION_T-M2D_LAION/best_checkpoint.pth
> ```

- `config.yml` is for CASTELLA. If you train models on Clotho-Moment, use `config-pretraining.yml`
- If you use pre-trained model weights, use `--resume ./**/{checkpoint}.pth`


1. Evaluation
Reproduce the evaluation on the `val` set.
```
python src/evaluate.py --config config.yml \
--model_path results/A-M2D_T-M2D/best_checkpoint.pth \
--feature_model_audio M2D --feature_model_text M2D
```
The result is:
```
2026-07-27 20:58:44.539:INFO:__main__ - Setup config, data and model...
['M2D']
2026-07-27 20:58:44.540:INFO:__main__ - setup model/optimizer/scheduler
2026-07-27 20:58:44.773:INFO:__main__ - CUDA enabled.
2026-07-27 20:58:46.002:INFO:__main__ - Model checkpoint: results/A-M2D_T-M2D/best_checkpoint.pth
2026-07-27 20:58:46.002:INFO:__main__ - Starting inference...
2026-07-27 20:58:46.002:INFO:__main__ - Generate submissions
compute st ed scores: 100%|█████████████████████████████████████████| 2/2 [00:01<00:00,  1.39it/s]
convert to multiples of clip_length=1: 100%|█████████████████| 352/352 [00:00<00:00, 16674.89it/s]
2026-07-27 20:58:47.461:INFO:__main__ - Saving/Evaluating before nms results
full: [0, 1500], 352/352=100.00 examples.
[eval_moment_retrieval] [full] 0.18 seconds
2026-07-27 20:58:47.658:INFO:__main__ - metrics_no_nms OrderedDict([   ('MR-full-R1@0.5', 53.69),
                ('MR-full-R1@0.7', 36.65),
                ('MR-full-mAP', 26.63),
                ('MR-full-mAP@0.5', 46.51),
                ('MR-full-mAP@0.75', 25.46)])

```

Reproduce the evaluation on the `test` set:
```
python src/evaluate.py --config config.yml --split test \
--model_path results/A-M2D_T-M2D/best_checkpoint.pth \
--feature_model_audio M2D --feature_model_text M2D
```
The result is:
```
2026-07-27 20:56:42.602:INFO:__main__ - Setup config, data and model...
['M2D']
2026-07-27 20:56:42.607:INFO:__main__ - setup model/optimizer/scheduler
2026-07-27 20:56:42.839:INFO:__main__ - CUDA enabled.
2026-07-27 20:56:44.301:INFO:__main__ - Model checkpoint: results/A-M2D_T-M2D/best_checkpoint.pth
2026-07-27 20:56:44.301:INFO:__main__ - Starting inference...
2026-07-27 20:56:44.301:INFO:__main__ - Generate submissions
compute st ed scores: 100%|████████████████████████████████████████████████| 6/6 [00:04<00:00,  1.22it/s]
convert to multiples of clip_length=1: 100%|██████████████████████| 1347/1347 [00:00<00:00, 19081.57it/s]
2026-07-27 20:56:49.297:INFO:__main__ - Saving/Evaluating before nms results
full: [0, 1500], 1347/1347=100.00 examples.
[eval_moment_retrieval] [full] 0.48 seconds
2026-07-27 20:56:49.802:INFO:__main__ - metrics_no_nms OrderedDict([   ('MR-full-R1@0.5', 43.88),
                ('MR-full-R1@0.7', 25.39),
                ('MR-full-mAP', 19.4),
                ('MR-full-mAP@0.5', 36.89),
                ('MR-full-mAP@0.75', 17.5)])

```

## Preparation for submission.jsonl
**Evaluation data for the submission, such as extracted features and `./data/dcase_evaluation.jsonl` will be publicly available on June 1.**

Download extracted features from [Zenodo](https://zenodo.org/records/20450254) or  [HuggingFace](https://huggingface.co/datasets/lighthouse-emnlp2024/AudioMomentRetrievalFromLongAudio_DCASE2026EvaluationData), and move them to `./features/clap` and `./features/clap_text`, and then run the following command to create a submission file. 
```
python src/create_submission.py --config config.yml \
--model_path results/A-M2D_T-M2D/best_checkpoint.pth \
--feature_model_audio M2D --feature_model_text M2D
```
You can get `submission.jsonl` file under `results` directory. For details, please read [this README.md](src/standalone_eval/README.md)

## Statistics of scores
Scores may vary slightly due to different random seeds or minor differences in library versions. We conducted five training runs, and the resulting scores on CASTELLA `test` set (mean ± standard deviation) are as follows:
- Only CASTELLA
  - R1@0.5    : 22.74±0.77
  - R1@0.7    : 10.17±0.86
  - mAP (avg)  : 10.49±0.53
  - mAP@0.5   : 21.93±0.57
  - mAP@0.75  : 8.85±0.58
- Clotho-Moment pre-training & CASTELLA fine-tuning
  - R1@0.5    : 25.86±0.74
  - R1@0.7    : 13.85±1.47
  - mAP (avg)  : 11.74±0.39
  - mAP@0.5   : 23.14±0.33
  - mAP@0.75  : 10.54±0.54

## Note
- This recipe includes minor changes from the original paper to improve performance:
  - Training extended from 100 to 200 epochs
  - window sampling controlled by `max_windows` to stabilize the training

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
# ---------------------------

# Citation
> S. Chunarkar, H. Krishnagiri, C. Lee, "Exploring Pretrained Audio-Text Encoders for Audio Moment Retrieval: DCASE 2026 Task 6," DCASE2026 Challenge, Tech. Rep., 2026.

```
@techreport{chunarkar2026_t6,
    Author = "Chunarkar, Snehit and Krishnagiri, Hamza and Lee, Chi-Chun",
    title = "Exploring Pretrained Audio-Text Encoders for Audio Moment Retrieval: DCASE 2026 Task 6",
    institution = "DCASE2026 Challenge",
    year = "2026",
    month = "June",
}
```
