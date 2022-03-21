#!/bin/bash
export install_path=/usr/local/Ascend

if [ -d ${install_path}/toolkit ]; then
    export LD_LIBRARY_PATH=/usr/include/hdf5/lib/:/usr/local/:/usr/local/lib/:/usr/lib/:${install_path}/fwkacllib/lib64/:${install_path}/driver/lib64/common/:${install_path}/driver/lib64/driver/:${install_path}/add-ons:${path_lib}:${LD_LIBRARY_PATH}
    export PATH=${install_path}/fwkacllib/ccec_compiler/bin:${install_path}/fwkacllib/bin:$PATH
    export PYTHONPATH=${install_path}/fwkacllib/python/site-packages:${install_path}/tfplugin/python/site-packages:${install_path}/toolkit/python/site-packages:$PYTHONPATH
    export PYTHONPATH=/usr/local/python3.7.5/lib/python3.7/site-packages:$PYTHONPATH
    export ASCEND_OPP_PATH=${install_path}/opp
else
    if [ -d ${install_path}/nnae/latest ];then
        export LD_LIBRARY_PATH=/usr/local/:/usr/local/python3.7.5/lib/:/usr/local/openblas/lib:/usr/local/lib/:/usr/lib64/:/usr/lib/:${install_path}/nnae/latest/fwkacllib/lib64/:${install_path}/driver/lib64/common/:${install_path}/driver/lib64/driver/:${install_path}/add-ons/:/usr/lib/aarch64_64-linux-gnu:$LD_LIBRARY_PATH
        export PATH=$PATH:${install_path}/nnae/latest/fwkacllib/ccec_compiler/bin/:${install_path}/nnae/latest/toolkit/tools/ide_daemon/bin/
        export ASCEND_OPP_PATH=${install_path}/nnae/latest/opp/
        export OPTION_EXEC_EXTERN_PLUGIN_PATH=${install_path}/nnae/latest/fwkacllib/lib64/plugin/opskernel/libfe.so:${install_path}/nnae/latest/fwkacllib/lib64/plugin/opskernel/libaicpu_engine.so:${install_path}/nnae/latest/fwkacllib/lib64/plugin/opskernel/libge_local_engine.so
        export PYTHONPATH=${install_path}/nnae/latest/fwkacllib/python/site-packages/:${install_path}/nnae/latest/fwkacllib/python/site-packages/auto_tune.egg/auto_tune:${install_path}/nnae/latest/fwkacllib/python/site-packages/schedule_search.egg:$PYTHONPATH
        export ASCEND_AICPU_PATH=${install_path}/nnae/latest
    else
        export LD_LIBRARY_PATH=/usr/local/:/usr/local/lib/:/usr/lib64/:/usr/lib/:/usr/local/python3.7.5/lib/:/usr/local/openblas/lib:${install_path}/ascend-toolkit/latest/fwkacllib/lib64/:${install_path}/driver/lib64/common/:${install_path}/driver/lib64/driver/:${install_path}/add-ons/:/usr/lib/aarch64-linux-gnu:$LD_LIBRARY_PATH
        export PATH=$PATH:${install_path}/ascend-toolkit/latest/fwkacllib/ccec_compiler/bin/:${install_path}/ascend-toolkit/latest/toolkit/tools/ide_daemon/bin/
        export ASCEND_OPP_PATH=${install_path}/ascend-toolkit/latest/opp/
        export OPTION_EXEC_EXTERN_PLUGIN_PATH=${install_path}/ascend-toolkit/latest/fwkacllib/lib64/plugin/opskernel/libfe.so:${install_path}/ascend-toolkit/latest/fwkacllib/lib64/plugin/opskernel/libaicpu_engine.so:${install_path}/ascend-toolkit/latest/fwkacllib/lib64/plugin/opskernel/libge_local_engine.so
        export PYTHONPATH=${install_path}/ascend-toolkit/latest/fwkacllib/python/site-packages/:${install_path}/ascend-toolkit/latest/fwkacllib/python/site-packages/auto_tune.egg/auto_tune:${install_path}/ascend-toolkit/latest/fwkacllib/python/site-packages/schedule_search.egg:$PYTHONPATH
        export ASCEND_AICPU_PATH=${install_path}/ascend-toolkit/latest
    fi
fi


#��Host��־���������,0-�ر�/1-����
export ASCEND_SLOG_PRINT_TO_STDOUT=1
#����Ĭ����־����,0-debug/1-info/2-warning/3-error
export ASCEND_GLOBAL_LOG_LEVEL=3
#����Host��Event��־������־,0-�ر�/1-����
export ASCEND_GLOBAL_EVENT_ENABLE=0
#�����Ƿ���taskque,0-�ر�/1-����
export TASK_QUEUE_ENABLE=1
#�����Ƿ���PTCopy,0-�ر�/1-����
export PTCOPY_ENABLE=1
#�����Ƿ���combined��־,0-�ر�/1-����
export COMBINED_ENABLE=1
#�������ⳡ���Ƿ���Ҫ���±���,����Ҫ�޸�
export DYNAMIC_OP="ADD#MUL"
#HCCL����������,1-�ر�/0-����
export HCCL_WHITELIST_DISABLE=1
#����Device����־�ȼ�Ϊerror
${install_path}/driver/tools/msnpureport -d 0 -g error
${install_path}/driver/tools/msnpureport -d 1 -g error
${install_path}/driver/tools/msnpureport -d 2 -g error
${install_path}/driver/tools/msnpureport -d 3 -g error
${install_path}/driver/tools/msnpureport -d 4 -g error
${install_path}/driver/tools/msnpureport -d 5 -g error
${install_path}/driver/tools/msnpureport -d 6 -g error
${install_path}/driver/tools/msnpureport -d 7 -g error
#�ر�Device��Event��־
${install_path}/driver/tools/msnpureport -e disable


path_lib=$(python3.7 -c """
import sys
import re
result=''
for index in range(len(sys.path)):
    match_sit = re.search('-packages', sys.path[index])
    if match_sit is not None:
        match_lib = re.search('lib', sys.path[index])

        if match_lib is not None:
            end=match_lib.span()[1]
            result += sys.path[index][0:end] + ':'

        result+=sys.path[index] + '/torch/lib:'
print(result)"""
)

echo ${path_lib}

export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib/:${path_lib}:$LD_LIBRARY_PATH