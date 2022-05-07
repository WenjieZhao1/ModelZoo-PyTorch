# BSD 3-Clause License
#
# Copyright (c) 2017 xxxx
# All rights reserved.
# Copyright 2021 Huawei Technologies Co., Ltd
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ============================================================================

import torch
from torch.nn.parallel.distributed import (DistributedDataParallel,
                                           _find_tensors)

from mmcv import print_log
from mmcv.utils import TORCH_VERSION
from .scatter_gather import scatter_kwargs


class MMDistributedDataParallel(DistributedDataParallel):
    """The DDP module that supports DataContainer.

    MMDDP has two main differences with PyTorch DDP:

    - It supports a custom type :class:`DataContainer` which allows more
      flexible control of input data.
    - It implement two APIs ``train_step()`` and ``val_step()``.
    """

    def scatter(self, inputs, kwargs, device_ids):
        return scatter_kwargs(inputs, kwargs, device_ids, dim=self.dim)

    def train_step(self, *inputs, **kwargs):
        """train_step() API for module wrapped by DistributedDataParallel.

        This method is basically the same as
        ``DistributedDataParallel.forward()``, while replacing
        ``self.module.forward()`` with ``self.module.train_step()``.
        It is compatible with PyTorch 1.1 - 1.5.
        """

        # In PyTorch >= 1.7, ``reducer._rebuild_buckets()`` is moved from the
        # end of backward to the beginning of forward.
        if (TORCH_VERSION >= '1.7' and 'parrots'
                not in TORCH_VERSION) and self.reducer._rebuild_buckets():
            print_log(
                'Reducer buckets have been rebuilt in this iteration.',
                logger='mmcv')

        if getattr(self, 'require_forward_param_sync', True):
            self._sync_params()

        # inputs, kwargs = self.scatter(inputs, kwargs, [-1])  # annoated by jyl
        # output = self.module.train_step(*inputs[0], **kwargs[0])  # annoated by jyl
        # forbid the first branch
        if self.device_ids and False:
            inputs, kwargs = self.scatter(inputs, kwargs, self.device_ids)
            if len(self.device_ids) == 1:
                output = self.module.train_step(*inputs[0], **kwargs[0])
            else:
                outputs = self.parallel_apply(
                    self._module_copies[:len(inputs)], inputs, kwargs)
                output = self.gather(outputs, self.output_device)
        else:
            inputs, kwargs = self.scatter(inputs, kwargs, [-1])
            output = self.module.train_step(*inputs[0], **kwargs[0])

        if torch.is_grad_enabled() and getattr(
                self, 'require_backward_grad_sync', True):
            if self.find_unused_parameters:
                self.reducer.prepare_for_backward(list(_find_tensors(output)))
            else:
                self.reducer.prepare_for_backward([])
        else:
            if TORCH_VERSION > '1.2':
                self.require_forward_param_sync = False
        return output

    def val_step(self, *inputs, **kwargs):
        """val_step() API for module wrapped by DistributedDataParallel.

        This method is basically the same as
        ``DistributedDataParallel.forward()``, while replacing
        ``self.module.forward()`` with ``self.module.val_step()``.
        It is compatible with PyTorch 1.1 - 1.5.
        """
        # In PyTorch >= 1.7, ``reducer._rebuild_buckets()`` is moved from the
        # end of backward to the beginning of forward.
        if (TORCH_VERSION >= '1.7' and 'parrots'
                not in TORCH_VERSION) and self.reducer._rebuild_buckets():
            print_log(
                'Reducer buckets have been rebuilt in this iteration.',
                logger='mmcv')

        if getattr(self, 'require_forward_param_sync', True):
            self._sync_params()
        if self.device_ids:
            inputs, kwargs = self.scatter(inputs, kwargs, self.device_ids)
            if len(self.device_ids) == 1:
                output = self.module.val_step(*inputs[0], **kwargs[0])
            else:
                outputs = self.parallel_apply(
                    self._module_copies[:len(inputs)], inputs, kwargs)
                output = self.gather(outputs, self.output_device)
        else:
            output = self.module.val_step(*inputs, **kwargs)

        if torch.is_grad_enabled() and getattr(
                self, 'require_backward_grad_sync', True):
            if self.find_unused_parameters:
                self.reducer.prepare_for_backward(list(_find_tensors(output)))
            else:
                self.reducer.prepare_for_backward([])
        else:
            if TORCH_VERSION > '1.2':
                self.require_forward_param_sync = False
        return output
