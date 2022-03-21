# Copyright 2020 Huawei Technologies Co., Ltd
from .test import multi_gpu_test, single_gpu_test
from .train import train_model

__all__ = [
    'train_model', 'init_recognizer', 'inference_recognizer', 'multi_gpu_test',
    'single_gpu_test'
]