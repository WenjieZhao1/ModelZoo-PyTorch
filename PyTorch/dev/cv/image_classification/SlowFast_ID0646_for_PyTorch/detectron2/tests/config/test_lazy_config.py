#
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
#
# Copyright (c) Facebook, Inc. and its affiliates.
import os
import unittest
import tempfile
from itertools import count

from detectron2.config import LazyConfig, LazyCall as L


class TestLazyPythonConfig(unittest.TestCase):
    def setUp(self):
        self.root_filename = os.path.join(os.path.dirname(__file__), "root_cfg.py")

    def test_load(self):
        cfg = LazyConfig.load(self.root_filename)

        self.assertEqual(cfg.dir1a_dict.a, "modified")
        self.assertEqual(cfg.dir1b_dict.a, 1)
        self.assertEqual(cfg.lazyobj.x, "base_a_1")

        cfg.lazyobj.x = "new_x"
        # reload
        cfg = LazyConfig.load(self.root_filename)
        self.assertEqual(cfg.lazyobj.x, "base_a_1")

    def test_save_load(self):
        cfg = LazyConfig.load(self.root_filename)
        with tempfile.TemporaryDirectory(prefix="detectron2") as d:
            fname = os.path.join(d, "test_config.yaml")
            LazyConfig.save(cfg, fname)
            cfg2 = LazyConfig.load(fname)

        self.assertEqual(cfg2.lazyobj._target_, "itertools.count")
        self.assertEqual(cfg.lazyobj._target_, count)
        cfg2.lazyobj.pop("_target_")
        cfg.lazyobj.pop("_target_")
        # the rest are equal
        self.assertEqual(cfg, cfg2)

    def test_overrides(self):
        cfg = LazyConfig.load(self.root_filename)
        LazyConfig.apply_overrides(cfg, ["lazyobj.x=123", 'dir1b_dict.a="123"'])
        self.assertEqual(cfg.dir1b_dict.a, "123")
        self.assertEqual(cfg.lazyobj.x, 123)

    def test_invalid_overrides(self):
        cfg = LazyConfig.load(self.root_filename)
        with self.assertRaises(KeyError):
            LazyConfig.apply_overrides(cfg, ["lazyobj.x.xxx=123"])

    def test_to_py(self):
        cfg = LazyConfig.load(self.root_filename)
        cfg.lazyobj.x = {"a": 1, "b": 2, "c": L(count)(x={"r": "a", "s": 2.4, "t": [1, 2, 3, "z"]})}
        cfg.list = ["a", 1, "b", 3.2]
        py_str = LazyConfig.to_py(cfg)
        expected = """cfg.dir1a_dict.a = "modified"
cfg.dir1a_dict.b = 2
cfg.dir1b_dict.a = 1
cfg.dir1b_dict.b = 2
cfg.lazyobj = itertools.count(
    x={
        "a": 1,
        "b": 2,
        "c": itertools.count(x={"r": "a", "s": 2.4, "t": [1, 2, 3, "z"]}),
    },
    y="base_a_1_from_b",
)
cfg.list = ["a", 1, "b", 3.2]
"""
        self.assertEqual(py_str, expected)