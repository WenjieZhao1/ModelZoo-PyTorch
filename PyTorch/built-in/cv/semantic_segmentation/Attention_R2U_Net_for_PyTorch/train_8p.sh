source ./npu_env.sh
a='R2AttU_Net'
python3 main_8p.py --model_type=$a --data_path="./dataset"