# Copyright 2021 Huawei Technologies Co., Ltd
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


import sys
import torch

sys.path.append('RawNet/python/RawNet2/Pre-trained_model')
from RawNet.python.RawNet2.parser import get_args
from model_RawNet2_original_code import RawNet

ptfile = "rawnet2_best_weights.pt"
args = get_args()
args.model['nb_classes'] = 6112
model = RawNet(args.model, device="cpu")
model.load_state_dict(torch.load(ptfile, map_location=torch.device('cpu')))
input_names = ["wav"]
output_names = ["class"]
dynamic_axes = {'wav': {0: '-1'}, 'class': {0: '-1'}}
dummy_input = torch.randn(1, 59049)
export_onnx_file = "RawNet2.onnx"
torch.onnx.export(model, dummy_input, export_onnx_file, input_names=input_names, dynamic_axes=dynamic_axes,
                  output_names=output_names, opset_version=11, verbose=True)
