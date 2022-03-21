#!/bin/bash

################�������ò�������Ҫģ�������޸�##################
# ��ѡ�ֶ�(�����ڴ˴�����Ĳ���): Network batch_size RANK_SIZE
# �������ƣ�ͬĿ¼����
Network="FOTS"
# ѵ��batch_size
batch_size=24
# ѵ��ʹ�õ�npu����
export RANK_SIZE=8
# ���ݼ�·��,����Ϊ��,����Ҫ�޸�
data_path=""

# ѵ��epoch
train_epochs=3
# ָ��ѵ����ʹ�õ�npu device��id
device_id=($(seq 0 7))
# �������ݽ�����
KERNEL_NUM=$(($(nproc)/8))

export MASTER_ADDR=localhost
export MASTER_PORT=22111
export HCCL_WHITELIST_DISABLE=1

KERNEL_NUM=$(($(nproc)/8))

NPUS=($(seq 0 7))
export NPU_WORLD_SIZE=${#NPUS[@]}
rank=0

# ����У�飬data_pathΪ�ش�������������������ɾ��ģ�������������˴������������������ж��岢��ֵ
for para in $*
do
    if [[ $para == --device_id* ]];then
        device_id=`echo ${para#*=}`
    elif [[ $para == --data_path* ]];then
        data_path=`echo ${para#*=}`
    fi
done

# У���Ƿ���data_path,����Ҫ�޸�
if [[ $data_path == "" ]];then
    echo "[Error] para \"data_path\" must be confing"
    exit 1
fi
# У���Ƿ�ָ����device_id,�ֶ�̬����device_id���ֶ�ָ��device_id,�˴�����Ҫ�޸�
if [ $ASCEND_DEVICE_ID ];then
    echo "device id is ${ASCEND_DEVICE_ID}"
elif [ ${device_id} ];then
    export ASCEND_DEVICE_ID=${device_id}
    echo "device id is 0-7"
else
    "[Error] device id must be config"
    exit 1
fi



###############ָ��ѵ���ű�ִ��·��###############
# cd����test�ļ���ͬ�㼶Ŀ¼��ִ�нű�����߼����ԣ�test_path_dirΪ����test�ļ��е�·��
cur_path=`pwd`
cur_path_last_dirname=${cur_path##*/}
if [ x"${cur_path_last_dirname}" == x"test" ];then
    test_path_dir=${cur_path}
    cd ..
    cur_path=`pwd`
else
    test_path_dir=${cur_path}/test
fi


#################������־���Ŀ¼������Ҫ�޸�#################
if [ -d ${test_path_dir}/output/${ASCEND_DEVICE_ID} ];then
    rm -rf ${test_path_dir}/output
    mkdir -p ${test_path_dir}/output
else
    mkdir -p ${test_path_dir}/output
fi


#################����ѵ���ű�#################
#ѵ����ʼʱ�䣬����Ҫ�޸�
start_time=$(date +%s)
# ��ƽ̨����ʱsource ��������
check_etp_flag=`env | grep etp_running_flag`
etp_flag=`echo ${check_etp_flag#*=}`
if [ x"${etp_flag}" != x"true" ];then
    source ${test_path_dir}/set_npu_env.sh
fi

for i in ${NPUS[@]}
do
    export NPU_CALCULATE_DEVICE=${i}
    export RANK=${rank}
    echo run process ${rank}
    
    PID_START=$((KERNEL_NUM * RANK))
    PID_END=$((PID_START + KERNEL_NUM - 1))

    time taskset -c $PID_START-$PID_END python3 ./train_8p.py --train-folder ${data_path} --continue-training --pf --batch-size ${batch_size} --batches-before-train 2\
    --num-workers $KERNEL_NUM > ${test_path_dir}/output/train_performance_${i}.log 2>&1 &
    let rank++
done