#!/usrbin/python
#encoding=utf-8
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

# Get n-gram propability from arpa file;

import re
import math

n_grams = ["unigram", 'bigram', 'trigram', '4gram', '5gram']

class LanguageModel:
    """
    New version of LanguageModel which can read the text arpa file ,which
    is generate from kennlm
    """
    def __init__(self, arpa_file=None, n_gram=2, start='<s>', end='</s>', unk='<unk>'):
        "Load arpa file to get words and prob"
        self.n_gram = n_gram
        self.start = start 
        self.end = end
        self.unk = unk
        self.scale = math.log(10)    #arpa格式是以10为底的对数概率，转化为以e为底
        self.initngrams(arpa_file)

    def initngrams(self, fn):
        "internal init of word bigrams"
        self.unigram = {}
        self.bigram = {}
        if self.n_gram == 3:
            self.trigrame = {}
        
	    # go through text and create each bigrams
        f = open(fn, 'r')
        recording = 0
        for lines in f.readlines():
            line = lines.strip('\n')
            #a = re.match('gram', line)
            if line == "\\1-grams:":
                recording = 1
                continue
            if line == "\\2-grams:":
                recording = 2
                continue
            if recording == 1:
                line = line.split('\t')
                if len(line) == 3:
                    self.unigram[line[1]] = [self.scale * float(line[0]), self.scale * float(line[2])]   #save the prob and backoff prob
                elif len(line) == 2:
                    self.unigram[line[1]] = [self.scale * float(line[0]), 0.0]
            if recording == 2:
                line = line.split('\t')
                if len(line) == 3:
                    #print(line[1])
                    self.bigram[line[1]] = [self.scale * float(line[0]), self.scale * float(line[2])]
                elif len(line) == 2:
                    self.bigram[line[1]] = [self.scale * float(line[0]), 0.0]
        f.close()
        self.unigram['UNK'] = self.unigram[self.unk]
        

    def get_uni_prob(self, wid):
        "Returns unigram probabiliy of word"
        return self.unigram[wid][0]
    
    def get_bi_prob(self, w1, w2):
        '''
        Return bigrams probability p(w2 | w1)
        if bigrame does not exist, use backoff prob
        '''
        if w1 == '':
            w1 = self.start
        if w2 == '':
            w2 = self.end
        key = w1 + ' ' + w2
        if key not in self.bigram:
            return self.unigram[w1][1] + self.unigram[w2][0]
        else:
            return self.bigram[key][0]

    def score_bg(self, sentence):
        '''
        Score a sentence using bigram, return P(sentence)
        '''
        val = 0.0
        words = sentence.strip().split()
        val += self.get_bi_prob(self.start, words[0])
        for i in range(len(words)-1):
            val += self.get_bi_prob(words[i], words[i+1])
        val += self.get_bi_prob(words[-1], self.end)
        return val

if __name__ == "__main__":
    lm = LanguageModel('./data_prepare/bigram.arpa')
    #print(lm.bigram['你 好'])
    print(lm.get_bi_prob('', 'sil'))
    #print(lm.score_bg("中国 呼吸"))

