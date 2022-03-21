#     Copyright [yyyy] [name of copyright owner]
#     Copyright 2020 Huawei Technologies Co., Ltd
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#



import logging

import cv2


def wait_key(target=None):
    key = cv2.waitKey() & 0xFF
    if target == None:
        return key
    if type(target) == str:
        target = ord(target)
    while key != target:
        key = cv2.waitKey() & 0xFF

    logging.debug('Key Pression caught:%s' % (target))