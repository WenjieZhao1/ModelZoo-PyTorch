#!/usr/bin/env bash
source test/env_npu.sh

data_path=""
for para in $*
do
    if [[ $para == --data_path* ]];then
        data_path=`echo ${para#*=}`
    fi
done

if [[ $data_path == "" ]];then
    echo "[Error] para \"data_path\" must be confing"
    exit 1
fi

nohup python3.7.5 -u train/main.py \
    --datadir ${data_path} \
    --decoder \
    --pretrainedEncoder "trained_models/erfnet_encoder_pretrained.pth.tar" \
    --num-epochs 3 \
    --amp \
    --opt-level "O2" \
    --loss-scale-value 128 > erfnet_1p_perf.log 2>&1 &