# Copyright 2020 Huawei Technologies Co., Ltd
from mmcv.utils import get_git_hash

import mmaction


def collect_env():
    env_info = collect_basic_env()
    env_info['MMAction2'] = (
        mmaction.__version__ + '+' + '9')
    return env_info


if __name__ == '__main__':
    for name, val in collect_env().items():
        print(f'{name}: {val}')