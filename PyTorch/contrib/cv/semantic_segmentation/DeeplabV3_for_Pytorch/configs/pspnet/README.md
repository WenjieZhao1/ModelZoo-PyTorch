# Pyramid Scene Parsing Network

## Introduction

<!-- [ALGORITHM] -->

```latex
@inproceedings{zhao2017pspnet,
  title={Pyramid Scene Parsing Network},
  author={Zhao, Hengshuang and Shi, Jianping and Qi, Xiaojuan and Wang, Xiaogang and Jia, Jiaya},
  booktitle={CVPR},
  year={2017}
}
```

## Results and models

### Cityscapes

| Method | Backbone  | Crop Size | Lr schd | Mem (GB) | Inf time (fps) |  mIoU | mIoU(ms+flip) | config                                                                                                                       | download                                                                                                                                                                                                                                                                                                                                                         |
| ------ | --------- | --------- | ------: | -------- | -------------- | ----: | ------------: | ---------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PSPNet | R-50-D8   | 512x1024  |   40000 | 6.1      | 4.07           | 77.85 |         79.18 | [config](   )   | [model](   ) &#124; [log](   )         |
| PSPNet | R-101-D8  | 512x1024  |   40000 | 9.6      | 2.68           | 78.34 |         79.74 | [config](   )  | [model](   ) &#124; [log](   )     |
| PSPNet | R-50-D8   | 769x769   |   40000 | 6.9      | 1.76           | 78.26 |         79.88 | [config](   )    | [model](   ) &#124; [log](   )             |
| PSPNet | R-101-D8  | 769x769   |   40000 | 10.9     | 1.15           | 79.08 |         80.28 | [config](   )   | [model](   ) &#124; [log](   )         |
| PSPNet | R-18-D8   | 512x1024  |   80000 | 1.7      | 15.71          | 74.87 |         76.04 | [config](   )   | [model](   ) &#124; [log](   )         |
| PSPNet | R-50-D8   | 512x1024  |   80000 | -        | -              | 78.55 |         79.79 | [config](   )   | [model](   ) &#124; [log](   )         |
| PSPNet | R-101-D8  | 512x1024  |   80000 | -        | -              | 79.76 |         81.01 | [config](   )  | [model](   ) &#124; [log](   )     |
| PSPNet | R-18-D8   | 769x769   |   80000 | 1.9      | 6.20           | 75.90 |         77.86 | [config](   )    | [model](   ) &#124; [log](   )             |
| PSPNet | R-50-D8   | 769x769   |   80000 | -        | -              | 79.59 |         80.69 | [config](   )    | [model](   ) &#124; [log](   )             |
| PSPNet | R-101-D8  | 769x769   |   80000 | -        | -              | 79.77 |         81.06 | [config](   )   | [model](   ) &#124; [log](   )         |
| PSPNet | R-18b-D8  | 512x1024  |   80000 | 1.5      | 16.28          | 74.23 |         75.79 | [config](   )  | [model](   ) &#124; [log](   )     |
| PSPNet | R-50b-D8  | 512x1024  |   80000 | 6.0      | 4.30           | 78.22 |         79.46 | [config](   )  | [model](   ) &#124; [log](   )     |
| PSPNet | R-101b-D8 | 512x1024  |   80000 | 9.5      | 2.76           | 79.69 |         80.79 | [config](   ) | [model](   ) &#124; [log](   ) |
| PSPNet | R-18b-D8  | 769x769   |   80000 | 1.7      | 6.41           | 74.92 |         76.90 | [config](   )   | [model](   ) &#124; [log](   )         |
| PSPNet | R-50b-D8  | 769x769   |   80000 | 6.8      | 1.88           | 78.50 |         79.96 | [config](   )   | [model](   ) &#124; [log](   )         |
| PSPNet | R-101b-D8 | 769x769   |   80000 | 10.8     | 1.17           | 78.87 |         80.04 | [config](   )  | [model](   ) &#124; [log](   )     |

### ADE20K

| Method | Backbone | Crop Size | Lr schd | Mem (GB) | Inf time (fps) |  mIoU | mIoU(ms+flip) | config                                                                                                                  | download                                                                                                                                                                                                                                                                                                                                     |
| ------ | -------- | --------- | ------: | -------- | -------------- | ----: | ------------: | ----------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PSPNet | R-50-D8  | 512x512   |   80000 | 8.5      | 23.53          | 41.13 |         41.94 | [config](   )   | [model](   ) &#124; [log](   )         |
| PSPNet | R-101-D8 | 512x512   |   80000 | 12       | 15.30          | 43.57 |         44.35 | [config](   )  | [model](   ) &#124; [log](   )     |
| PSPNet | R-50-D8  | 512x512   |  160000 | -        | -              | 42.48 |         43.44 | [config](   )  | [model](   ) &#124; [log](   )     |
| PSPNet | R-101-D8 | 512x512   |  160000 | -        | -              | 44.39 |         45.35 | [config](   ) | [model](   ) &#124; [log](   ) |

### Pascal VOC 2012 + Aug

| Method | Backbone | Crop Size | Lr schd | Mem (GB) | Inf time (fps) |  mIoU | mIoU(ms+flip) | config                                                                                                                   | download                                                                                                                                                                                                                                                                                                                                         |
| ------ | -------- | --------- | ------: | -------- | -------------- | ----: | ------------: | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PSPNet | R-50-D8  | 512x512   |   20000 | 6.1      | 23.59          | 76.78 |         77.61 | [config](   )  | [model](   ) &#124; [log](   )     |
| PSPNet | R-101-D8 | 512x512   |   20000 | 9.6      | 15.02          | 78.47 |         79.25 | [config](   ) | [model](   ) &#124; [log](   ) |
| PSPNet | R-50-D8  | 512x512   |   40000 | -        | -              | 77.29 |         78.48 | [config](   )  | [model](   ) &#124; [log](   )     |
| PSPNet | R-101-D8 | 512x512   |   40000 | -        | -              | 78.52 |         79.57 | [config](   ) | [model](   ) &#124; [log](   ) |

### Pascal Context

| Method | Backbone | Crop Size | Lr schd | Mem (GB) | Inf time (fps) |  mIoU | mIoU(ms+flip) | config                                                                                                                         | download                                                                                                                                                                                                                                                                                                                                                                 |
| ------ | -------- | --------- | ------: | -------- | -------------- | ----: | ------------: | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PSPNet | R-101-D8 | 480x480   |   40000 | 8.8      | 9.68           | 46.60 |         47.78 | [config](   ) | [model](   ) &#124; [log](   ) |
| PSPNet | R-101-D8 | 480x480   |   80000 | -        | -              | 46.03 |         47.15 | [config](   ) | [model](   ) &#124; [log](   ) |

### Pascal Context 59

| Method | Backbone | Crop Size | Lr schd | Mem (GB) | Inf time (fps) |  mIoU | mIoU(ms+flip) | config                                                                                                                         | download                                                                                                                                                                                                                                                                                                                                                                 |
| ------ | -------- | --------- | ------: | -------- | -------------- | ----: | ------------: | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PSPNet | R-101-D8 | 480x480   |   40000 | -      | -           | 52.02 |         53.54 | [config](   ) | [model](   ) &#124; [log](   ) |
| PSPNet | R-101-D8 | 480x480   |   80000 | -        | -              | 52.47 |         53.99 | [config](   ) | [model](   ) &#124; [log](   ) |