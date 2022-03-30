# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
import cv2
import torch
from torch import nn
from detectron2.utils.comm import get_world_size
from detectron2.structures import pairwise_iou, Boxes
# from .data import CenterNetCrop
import torch.nn.functional as F
import numpy as np
from detectron2.structures import Boxes, ImageList, Instances

__all__ = ['reduce_sum', '_transpose']

INF = 1000000000

def _transpose(training_targets, num_loc_list):
    '''
    This function is used to transpose image first training targets to 
        level first ones
    :return: level first training targets
    '''
    for im_i in range(len(training_targets)):
        training_targets[im_i] = torch.split(
            training_targets[im_i], num_loc_list, dim=0)

    targets_level_first = []
    for targets_per_level in zip(*training_targets):
        targets_level_first.append(
            torch.cat(targets_per_level, dim=0))
    return targets_level_first


def reduce_sum(tensor):
    world_size = get_world_size()
    if world_size < 2:
        return tensor
    tensor = tensor.clone()
    torch.distributed.all_reduce(tensor, op=torch.distributed.ReduceOp.SUM)
    return tensor