PORT=29888 ./tools/dist_train.sh ./configs/fcos/fcos_r50_caffe_fpn_4x4_1x_coco.py 8 --npu-ids 0 --cfg-options optimizer.lr=0.01 --seed 0 --opt-level O1 --loss-scale 32.0