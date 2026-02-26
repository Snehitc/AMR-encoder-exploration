# dcase2026_task6_baseline
DETR-based baseline for DCASE 2026 challenge task 6.

## Getting started
0. Clone this repository
```
git clone https://github.com/awkrail/dcase2026_task6_baseline.git
```
1. Install Pytorch & depndency libraries
Install pytorch, torchvision, and torchaudio based on your GPU environments. Note that the inference API is available for CPU environments. We tested the codes on Python 3.9 and CUDA 11.8:
```
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118
pip install -r requirement.txt
```
2. Prepare feature files
Download [CASTELLA dataset](https://zenodo.org/records/17412176).
```
wget https://zenodo.org/records/17412176/files/features.tar.gz
tar -zxvf features.tar.gz
```

## Training and evaluation
0. Train a model
```
bash scripts/train.sh
```

1. Evaluation
```
bash scripts/eval.sh
```

## Citation
If you find this code useful for your research, please cite this repo:
```
@misc{dcase2026baseline_task6,
  author = {Taichi Nishimura},
  title = {dcase2026_task6_baseline},
  year = {2026},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/awkrail/dcase2026_task6_baseline}}
}
```

## Others
This code is based on [lighthouse](https://github.com/line/lighthouse).


## Contact
taichitary@gmail.com
