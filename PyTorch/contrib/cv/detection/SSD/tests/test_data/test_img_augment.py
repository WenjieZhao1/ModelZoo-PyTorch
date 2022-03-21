# Copyright 2021 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import copy

import mmcv
import numpy as np
from mmcv.utils import build_from_cfg
from numpy.testing import assert_array_equal

from mmdet.core.mask import BitmapMasks, PolygonMasks
from mmdet.datasets.builder import PIPELINES


def construct_toy_data(poly2mask=True):
    img = np.array([[1, 2, 3, 4], [5, 6, 7, 8]], dtype=np.uint8)
    img = np.stack([img, img, img], axis=-1)
    results = dict()
    # image
    results['img'] = img
    results['img_shape'] = img.shape
    results['img_fields'] = ['img']
    # bboxes
    results['bbox_fields'] = ['gt_bboxes', 'gt_bboxes_ignore']
    results['gt_bboxes'] = np.array([[0., 0., 2., 1.]], dtype=np.float32)
    results['gt_bboxes_ignore'] = np.array([[2., 0., 3., 1.]],
                                           dtype=np.float32)
    # labels
    results['gt_labels'] = np.array([1], dtype=np.int64)
    # masks
    results['mask_fields'] = ['gt_masks']
    if poly2mask:
        gt_masks = np.array([[0, 1, 1, 0], [0, 1, 0, 0]],
                            dtype=np.uint8)[None, :, :]
        results['gt_masks'] = BitmapMasks(gt_masks, 2, 4)
    else:
        raw_masks = [[np.array([1, 0, 2, 0, 2, 1, 1, 1], dtype=np.float)]]
        results['gt_masks'] = PolygonMasks(raw_masks, 2, 4)
    # segmentations
    results['seg_fields'] = ['gt_semantic_seg']
    results['gt_semantic_seg'] = img[..., 0]
    return results


def test_adjust_color():
    results = construct_toy_data()
    # test wighout aug
    transform = dict(type='ColorTransform', prob=0, level=10)
    transform_module = build_from_cfg(transform, PIPELINES)
    results_transformed = transform_module(copy.deepcopy(results))
    assert_array_equal(results_transformed['img'], results['img'])

    # test with factor 1
    img = results['img']
    transform = dict(type='ColorTransform', prob=1, level=10)
    transform_module = build_from_cfg(transform, PIPELINES)
    results_transformed = transform_module(copy.deepcopy(results))
    assert_array_equal(results_transformed['img'], img)

    # test with factor 0
    transform_module.factor = 0
    img_gray = mmcv.bgr2gray(img.copy())
    img_r = np.stack([img_gray, img_gray, img_gray], axis=-1)
    results_transformed = transform_module(copy.deepcopy(results))
    assert_array_equal(results_transformed['img'], img_r)

    # test with factor 0.5
    transform_module.factor = 0.5
    results_transformed = transform_module(copy.deepcopy(results))
    img = results['img']
    assert_array_equal(
        results_transformed['img'],
        np.round(np.clip((img * 0.5 + img_r * 0.5), 0, 255)).astype(img.dtype))


def test_imequalize(nb_rand_test=100):

    def _imequalize(img):
        # equalize the image using PIL.ImageOps.equalize
        from PIL import ImageOps, Image
        img = Image.fromarray(img)
        equalized_img = np.asarray(ImageOps.equalize(img))
        return equalized_img

    results = construct_toy_data()
    # test wighout aug
    transform = dict(type='EqualizeTransform', prob=0)
    transform_module = build_from_cfg(transform, PIPELINES)
    results_transformed = transform_module(copy.deepcopy(results))
    assert_array_equal(results_transformed['img'], results['img'])

    # test equalize with case step=0
    transform = dict(type='EqualizeTransform', prob=1.)
    transform_module = build_from_cfg(transform, PIPELINES)
    img = np.array([[0, 0, 0], [120, 120, 120], [255, 255, 255]],
                   dtype=np.uint8)
    img = np.stack([img, img, img], axis=-1)
    results['img'] = img
    results_transformed = transform_module(copy.deepcopy(results))
    assert_array_equal(results_transformed['img'], img)

    # test equalize with randomly sampled image.
    for _ in range(nb_rand_test):
        img = np.clip(np.random.uniform(0, 1, (1000, 1200, 3)) * 260, 0,
                      255).astype(np.uint8)
        results['img'] = img
        results_transformed = transform_module(copy.deepcopy(results))
        assert_array_equal(results_transformed['img'], _imequalize(img))


def test_adjust_brightness(nb_rand_test=100):

    def _adjust_brightness(img, factor):
        # adjust the brightness of image using
        # PIL.ImageEnhance.Brightness
        from PIL.ImageEnhance import Brightness
        from PIL import Image
        img = Image.fromarray(img)
        brightened_img = Brightness(img).enhance(factor)
        return np.asarray(brightened_img)

    results = construct_toy_data()
    # test wighout aug
    transform = dict(type='BrightnessTransform', level=10, prob=0)
    transform_module = build_from_cfg(transform, PIPELINES)
    results_transformed = transform_module(copy.deepcopy(results))
    assert_array_equal(results_transformed['img'], results['img'])

    # test case with factor 1.0
    transform = dict(type='BrightnessTransform', level=10, prob=1.)
    transform_module = build_from_cfg(transform, PIPELINES)
    transform_module.factor = 1.0
    results_transformed = transform_module(copy.deepcopy(results))
    assert_array_equal(results_transformed['img'], results['img'])

    # test case with factor 0.0
    transform_module.factor = 0.0
    results_transformed = transform_module(copy.deepcopy(results))
    assert_array_equal(results_transformed['img'],
                       np.zeros_like(results['img']))

    # test with randomly sampled images and factors.
    for _ in range(nb_rand_test):
        img = np.clip(np.random.uniform(0, 1, (1000, 1200, 3)) * 260, 0,
                      255).astype(np.uint8)
        factor = np.random.uniform()
        transform_module.factor = factor
        results['img'] = img
        np.testing.assert_allclose(
            transform_module(copy.deepcopy(results))['img'].astype(np.int32),
            _adjust_brightness(img, factor).astype(np.int32),
            rtol=0,
            atol=1)


def test_adjust_contrast(nb_rand_test=100):

    def _adjust_contrast(img, factor):
        from PIL.ImageEnhance import Contrast
        from PIL import Image
        # Image.fromarray defaultly supports RGB, not BGR.
        # convert from BGR to RGB
        img = Image.fromarray(img[..., ::-1], mode='RGB')
        contrasted_img = Contrast(img).enhance(factor)
        # convert from RGB to BGR
        return np.asarray(contrasted_img)[..., ::-1]

    results = construct_toy_data()
    # test wighout aug
    transform = dict(type='ContrastTransform', level=10, prob=0)
    transform_module = build_from_cfg(transform, PIPELINES)
    results_transformed = transform_module(copy.deepcopy(results))
    assert_array_equal(results_transformed['img'], results['img'])

    # test case with factor 1.0
    transform = dict(type='ContrastTransform', level=10, prob=1.)
    transform_module = build_from_cfg(transform, PIPELINES)
    transform_module.factor = 1.0
    results_transformed = transform_module(copy.deepcopy(results))
    assert_array_equal(results_transformed['img'], results['img'])

    # test case with factor 0.0
    transform_module.factor = 0.0
    results_transformed = transform_module(copy.deepcopy(results))
    np.testing.assert_allclose(
        results_transformed['img'],
        _adjust_contrast(results['img'], 0.),
        rtol=0,
        atol=1)

    # test adjust_contrast with randomly sampled images and factors.
    for _ in range(nb_rand_test):
        img = np.clip(np.random.uniform(0, 1, (1200, 1000, 3)) * 260, 0,
                      255).astype(np.uint8)
        factor = np.random.uniform()
        transform_module.factor = factor
        results['img'] = img
        results_transformed = transform_module(copy.deepcopy(results))
        # Note the gap (less_equal 1) between PIL.ImageEnhance.Contrast
        # and mmcv.adjust_contrast comes from the gap that converts from
        # a color image to gray image using mmcv or PIL.
        np.testing.assert_allclose(
            transform_module(copy.deepcopy(results))['img'].astype(np.int32),
            _adjust_contrast(results['img'], factor).astype(np.int32),
            rtol=0,
            atol=1)