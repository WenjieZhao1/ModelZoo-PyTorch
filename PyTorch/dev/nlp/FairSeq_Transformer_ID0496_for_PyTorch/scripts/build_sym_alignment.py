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
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""
Use this script in order to build symmetric alignments for your translation
dataset.
This script depends on fast_align and mosesdecoder tools. You will need to
build those before running the script.
fast_align:
    github: http://github.com/clab/fast_align
    instructions: follow the instructions in README.md
mosesdecoder:
    github: http://github.com/moses-smt/mosesdecoder
    instructions: http://www.statmt.org/moses/?n=Development.GetStarted
The script produces the following files under --output_dir:
    text.joined - concatenation of lines from the source_file and the
    target_file.
    align.forward - forward pass of fast_align.
    align.backward - backward pass of fast_align.
    aligned.sym_heuristic - symmetrized alignment.
"""

import argparse
import os
from itertools import zip_longest


def main():
    parser = argparse.ArgumentParser(description='symmetric alignment builer')
    # fmt: off
    parser.add_argument('--fast_align_dir',
                        help='path to fast_align build directory')
    parser.add_argument('--mosesdecoder_dir',
                        help='path to mosesdecoder root directory')
    parser.add_argument('--sym_heuristic',
                        help='heuristic to use for symmetrization',
                        default='grow-diag-final-and')
    parser.add_argument('--source_file',
                        help='path to a file with sentences '
                             'in the source language')
    parser.add_argument('--target_file',
                        help='path to a file with sentences '
                             'in the target language')
    parser.add_argument('--output_dir',
                        help='output directory')
    # fmt: on
    args = parser.parse_args()

    fast_align_bin = os.path.join(args.fast_align_dir, 'fast_align')
    symal_bin = os.path.join(args.mosesdecoder_dir, 'bin', 'symal')
    sym_fast_align_bin = os.path.join(
        args.mosesdecoder_dir, 'scripts', 'ems',
        'support', 'symmetrize-fast-align.perl')

    # create joined file
    joined_file = os.path.join(args.output_dir, 'text.joined')
    with open(args.source_file, 'r', encoding='utf-8') as src, open(args.target_file, 'r', encoding='utf-8') as tgt:
        with open(joined_file, 'w', encoding='utf-8') as joined:
            for s, t in zip_longest(src, tgt):
                print('{} ||| {}'.format(s.strip(), t.strip()), file=joined)

    bwd_align_file = os.path.join(args.output_dir, 'align.backward')

    # run forward alignment
    fwd_align_file = os.path.join(args.output_dir, 'align.forward')
    fwd_fast_align_cmd = '{FASTALIGN} -i {JOINED} -d -o -v > {FWD}'.format(
        FASTALIGN=fast_align_bin,
        JOINED=joined_file,
        FWD=fwd_align_file)
    assert os.system(fwd_fast_align_cmd) == 0

    # run backward alignment
    bwd_align_file = os.path.join(args.output_dir, 'align.backward')
    bwd_fast_align_cmd = '{FASTALIGN} -i {JOINED} -d -o -v -r > {BWD}'.format(
        FASTALIGN=fast_align_bin,
        JOINED=joined_file,
        BWD=bwd_align_file)
    assert os.system(bwd_fast_align_cmd) == 0

    # run symmetrization
    sym_out_file = os.path.join(args.output_dir, 'aligned')
    sym_cmd = '{SYMFASTALIGN} {FWD} {BWD} {SRC} {TGT} {OUT} {HEURISTIC} {SYMAL}'.format(
        SYMFASTALIGN=sym_fast_align_bin,
        FWD=fwd_align_file,
        BWD=bwd_align_file,
        SRC=args.source_file,
        TGT=args.target_file,
        OUT=sym_out_file,
        HEURISTIC=args.sym_heuristic,
        SYMAL=symal_bin
    )
    assert os.system(sym_cmd) == 0


if __name__ == '__main__':
    main()