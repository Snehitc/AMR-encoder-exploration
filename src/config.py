"""
Copyright $today.year LY Corporation

LY Corporation licenses this file to you under the Apache License,
version 2.0 (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at:

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

import os
import time
import torch
import argparse
import shutil
import yaml
import copy

from basic_utils import mkdirp, load_json, save_json, make_zipfile, dict_to_markdown
from easydict import EasyDict

# [Modified by Snehit]: create ensemble features dirs
class BaseOptions(object):
    def __init__(self, args):
        self.config_path = args.config
        self.feature_model_audio = args.feature_model_audio
        self.feature_model_text = args.feature_model_text
        self.opt = {}


    @property
    def option(self):
        if len(self.opt) == 0:
            raise RuntimeError('option is empty. Did you run parse()?')
        return self.opt


    def update(self, yaml_file):
        with open(yaml_file, 'r') as f:
            yml = yaml.load(f, Loader=yaml.FullLoader)
            self.opt.update(yml)


    def parse(self):
        with open(self.config_path, 'r') as f:
            yml = yaml.load(f, Loader=yaml.FullLoader)
            self.opt.update(yml)

        self.opt = EasyDict(self.opt)
        self.opt.feat_model_combination = f"A-{'_'.join(self.feature_model_audio)}_T-{'_'.join(self.feature_model_text)}"
        self.opt.feature_model_audio = self.feature_model_audio
        self.opt.feature_model_text = self.feature_model_text

        self.opt.ckpt_filepath = os.path.join(self.opt.results_dir, self.opt.feat_model_combination, self.opt.ckpt_filename)
        os.makedirs(os.path.dirname(self.opt.ckpt_filepath), exist_ok=True)

        self.opt.train_log_filepath = os.path.join(self.opt.results_dir, self.opt.feat_model_combination, self.opt.train_log_filename)
        os.makedirs(os.path.dirname(self.opt.train_log_filepath), exist_ok=True)

        self.opt.eval_log_filepath = os.path.join(self.opt.results_dir, self.opt.feat_model_combination, self.opt.eval_log_filename)
        os.makedirs(os.path.dirname(self.opt.eval_log_filepath), exist_ok=True)
