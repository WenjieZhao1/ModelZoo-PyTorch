[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/camera-distance-aware-top-down-approach-for/root-joint-localization-on-human3-6m)](https://paperswithcode.com/sota/root-joint-localization-on-human3-6m?p=camera-distance-aware-top-down-approach-for)

[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/camera-distance-aware-top-down-approach-for/3d-multi-person-pose-estimation-absolute-on)](https://paperswithcode.com/sota/3d-multi-person-pose-estimation-absolute-on?p=camera-distance-aware-top-down-approach-for)

[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/camera-distance-aware-top-down-approach-for/3d-multi-person-pose-estimation-root-relative)](https://paperswithcode.com/sota/3d-multi-person-pose-estimation-root-relative?p=camera-distance-aware-top-down-approach-for)

# RootNet of "Camera Distance-aware Top-down Approach for 3D Multi-person Pose Estimation from a Single RGB Image"

<p align="center">
<img src="assets/qualitative_intro.PNG" width="800" height="300">
</p>

<p align="middle">
<img src="assets/posetrack_1.gif" width="200" height="150"> <img src="assets/posetrack_2.gif" width="200" height="150"><img src="assets/posetrack_3.gif" width="200" height="150"> <img src="assets/posetrack_4.gif" width="200" height="150">
</p>

## Introduction

This repo is official **[PyTorch](https://pytorch.org)** implementation of **[Camera Distance-aware Top-down Approach for 3D Multi-person Pose Estimation from a Single RGB Image (ICCV 2019)](https://arxiv.org/abs/1907.11346)**. It contains **RootNet** part.

**What this repo provides:**
* [PyTorch](https://pytorch.org) implementation of [Camera Distance-aware Top-down Approach for 3D Multi-person Pose Estimation from a Single RGB Image (ICCV 2019)](https://arxiv.org/abs/1907.11346).
* Flexible and simple code.
* Human pose estimation visualization code.

## Dependencies
* [PyTorch](https://pytorch.org)
* [Anaconda](https://www.anaconda.com/download/)
* [COCO API](https://github.com/cocodataset/cocoapi)

This code is tested under Ubuntu 16.04, CUDA 9.0, cuDNN 7.1 environment with two NVIDIA 1080Ti GPUs.

Python 3.6.5 version with Anaconda 3 is used for development.

## Quick demo
You can try quick demo at `demo` folder. 
* Prepare `input.jpg` and pre-trained snapshot at `demo` folder.
* Set `bbox_list` at [here](https://github.com/mks0601/3DMPPE_ROOTNET_RELEASE/blob/ca25760a2d60272a5952cd6612a69b65dc926be3/demo/demo.py#L62).
* Run `python demo.py --gpu 0 --test_epoch 18` if you want to run on gpu 0.
* You can see `output_root_2d.jpg` and printed root joint depths.

## Directory

### Root
The `${POSE_ROOT}` is described as below.
```
${POSE_ROOT}
|-- data
|-- demo
|-- common
|-- main
|-- output
```
* `data` contains data loading codes and soft links to images and annotations directories.
* `demo` contains demo codes.
* `common` contains kernel codes for 3d multi-person pose estimation system.
* `main` contains high-level codes for training or testing the network.
* `output` contains log, trained models, visualized outputs, and test result.

### Data
You need to follow directory structure of the `data` as below.
```
${POSE_ROOT}
|-- data
|   |-- Human36M
|   |   |-- bbox
|   |   |   |-- bbox_human36m_output.json
|   |   |-- images
|   |   |-- annotations
|   |-- MPII
|   |   |-- images
|   |   |-- annotations
|   |-- MSCOCO
|   |   |-- images
|   |   |   |-- train2017
|   |   |   |-- val2017
|   |   |-- annotations
|   |-- MuCo
|   |   |-- data
|   |   |   |-- augmented_set
|   |   |   |-- unaugmented_set
|   |   |   |-- MuCo-3DHP.json
|   |-- MuPoTS
|   |   |-- bbox
|   |   |   |-- bbox_mupots_output.json
|   |   |-- data
|   |   |   |-- MultiPersonTestSet
|   |   |   |-- MuPoTS-3D.json
|   |-- PW3D
|   |   |-- data
|   |   |   |-- 3DPW_train.json
|   |   |   |-- 3DPW_validation.json
|   |   |   |-- 3DPW_test.json
|   |   |-- imageFiles
```

If you have a problem with 'Download limit' problem when tried to download dataset from google drive link, please try this trick.  
```  
* Go the shared folder, which contains files you want to copy to your drive  
* Select all the files you want to copy  
* In the upper right corner click on three vertical dots and select “make a copy”  
* Then, the file is copied to your personal google drive account. You can download it from your personal account.  
```  

### Output
You need to follow the directory structure of the `output` folder as below.
```
${POSE_ROOT}
|-- output
|-- |-- log
|-- |-- model_dump
|-- |-- result
|-- |-- vis
```
* Creating `output` folder as soft link form is recommended instead of folder form because it would take large storage capacity.
* `log` folder contains training log file.
* `model_dump` folder contains saved checkpoints for each epoch.
* `result` folder contains final estimation files generated in the testing stage.
* `vis` folder contains visualized results.

## Running 3DMPPE_ROOTNET
### Start
* In the `main/config.py`, you can change settings of the model including dataset to use, network backbone, and input size and so on.
* **YOU MUST SET `bbox_real` according to unit of each dataset. For example, Human3.6M uses milimeter, therefore `bbox_real = (2000, 2000)`. 3DPW uses meter, therefore `bbox_real = (2, 2)`.**

### Train
In the `main` folder, run
```bash
python train.py --gpu 0-1
```
to train the network on the GPU 0,1. 

If you want to continue experiment, run 
```bash
python train.py --gpu 0-1 --continue
```
`--gpu 0,1` can be used instead of `--gpu 0-1`.

### Test
Place trained model at the `output/model_dump/`.

In the `main` folder, run 
```bash
python test.py --gpu 0-1 --test_epoch 20
```
to test the network on the GPU 0,1 with 20th epoch trained model. `--gpu 0,1` can be used instead of `--gpu 0-1`.

## Results
 
For the evaluation, you can run `test.py` or there are evaluation codes in `Human36M` and `MuPoTS`.

#### Human3.6M dataset using protocol 2 (milimeter)

| Method    | MRPE | MRPE_x | MRPE_y | MRPE_z | 
|-----------|-------|-------|--------|--------|
| RootNet |  120.0 | 23.3 |  23.0 |  108.1 |



#### MuPoTS-3D dataset (percentage)

| Method    | AP_25 | 
|-----------|-------|
| RootNet |  31.0 | 

#### 3DPW dataset (test set. meter)

| Method    | MRPE | MRPE_x | MRPE_y | MRPE_z | 
|-----------|-------|-------|--------|--------|
| RootNet |  0.386 | 0.045 |  0.094 |  0.353 |

### MSCOCO dataset

We additionally provide estimated 3D human root coordinates in on the MSCOCO dataset. The coordinates are in 3D camera coordinate system, and focal lengths are set to 1500mm for both x and y axis. You can change focal length and corresponding distance using equation 2 or equation in supplementarial material of my [paper](https://arxiv.org/abs/1907.11346).

## Reference
  ```
@InProceedings{Moon_2019_ICCV_3DMPPE,
  author = {Moon, Gyeongsik and Chang, Juyong and Lee, Kyoung Mu},
  title = {Camera Distance-aware Top-down Approach for 3D Multi-person Pose Estimation from a Single RGB Image},
  booktitle = {The IEEE Conference on International Conference on Computer Vision (ICCV)},
  year = {2019}
}
```
