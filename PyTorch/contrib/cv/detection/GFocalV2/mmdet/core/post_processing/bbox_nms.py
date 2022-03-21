# Copyright 2021 Huawei Technologies Co., Ltd
#
# Licensed under the BSD 3-Clause License  (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://opensource.org/licenses/BSD-3-Clause
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import torch
from mmcv.ops.nms import batched_nms

from mmdet.core.bbox.iou_calculators import bbox_overlaps

class BatchNMSOp(torch.autograd.Function):
    @staticmethod
    def forward(ctx, bboxes, scores, score_threshold, iou_threshold, max_size_per_class, max_total_size):
        """
        boxes (torch.Tensor): boxes in shape (1, N, C, 4).
        scores (torch.Tensor): scores in shape (1, N, C).
        return:
            nmsed_boxes: (1, N, 4)
            nmsed_scores: (1, N)
            nmsed_classes: (1, N)
            nmsed_num: (1,)
        """
        try:
            bboxes = bboxes.to("npu")
            scores = scores.to("npu")
            nmsed_boxes, nmsed_scores, nmsed_classes, nmsed_num = \
                torch.npu_batch_nms(bboxes, scores, score_threshold, iou_threshold, max_size_per_class, max_total_size)
            nmsed_boxes = nmsed_boxes.to("cpu")
            nmsed_scores = nmsed_scores.to("cpu")
            nmsed_classes = nmsed_classes.to("cpu")
            nmsed_num = nmsed_num.to("cpu")
        except:
            # pytorch2onnx phony implement
            nmsed_boxes = bboxes[:, :max_total_size, 0, :]
            nmsed_scores = scores[:, :max_total_size, 0]
            nmsed_classes = torch.arange(max_total_size, dtype=torch.long)
            nmsed_num = torch.Tensor([max_total_size])
        return nmsed_boxes, nmsed_scores, nmsed_classes, nmsed_num

    @staticmethod
    def symbolic(g, bboxes, scores, score_thr, iou_thr, max_size_p_class, max_t_size):
        nmsed_boxes, nmsed_scores, nmsed_classes, nmsed_num = g.op('BatchMultiClassNMS',
            bboxes, scores, score_threshold_f=score_thr, iou_threshold_f=iou_thr,
            max_size_per_class_i=max_size_p_class, max_total_size_i=max_t_size, outputs=4)
        return nmsed_boxes, nmsed_scores, nmsed_classes, nmsed_num


def batch_nms_op(bboxes, scores, score_threshold, iou_threshold, max_size_per_class, max_total_size):
    """
    boxes (torch.Tensor): boxes in shape (N, 4).
    scores (torch.Tensor): scores in shape (N, ).
    """
    if bboxes.dtype == torch.float32:
        bboxes = bboxes.reshape(1, bboxes.shape[0], -1, 4).half()
        scores = scores.reshape(1, scores.shape[0], -1).half()
    else:
        bboxes = bboxes.reshape(1, bboxes.shape[0], -1, 4)
        scores = scores.reshape(1, scores.shape[0], -1)
    nmsed_boxes, nmsed_scores, nmsed_classes, nmsed_num = BatchNMSOp.apply(bboxes, scores,
        score_threshold, iou_threshold, max_size_per_class, max_total_size)
    nmsed_boxes = nmsed_boxes.float()
    nmsed_scores = nmsed_scores.float()
    nmsed_classes = nmsed_classes.long()
    dets = torch.cat((nmsed_boxes.reshape((max_total_size, 4)), nmsed_scores.reshape((max_total_size, 1))), -1)
    labels = nmsed_classes.reshape((max_total_size, ))
    return dets, labels

def multiclass_nms_npu(multi_bboxes,  # [1000, 320] [4693, 4]
                   multi_scores,  # [1000, 81]
                   score_thr,     # 0.05
                   nms_cfg,       # 0.5
                   max_num=-1,    # 100
                   score_factors=None,
                   return_inds=False):
    num_classes = multi_scores.size(1) - 1
    bboxes = multi_bboxes.reshape((5000, 1, 4))
    scores = multi_scores[:, :-1]  # [1000, 80]
    if score_factors is not None:
        scores = scores * score_factors[:, None]

    """npu with custom op"""
    dets, labels = batch_nms_op(bboxes, scores, score_thr, nms_cfg.get("iou_threshold"), max_num, max_num)
    return dets, labels

def multiclass_nms(multi_bboxes,
                   multi_scores,
                   score_thr,
                   nms_cfg,
                   max_num=-1,
                   score_factors=None,
                   return_inds=False):
    """NMS for multi-class bboxes.

    Args:
        multi_bboxes (Tensor): shape (n, #class*4) or (n, 4)
        multi_scores (Tensor): shape (n, #class), where the last column
            contains scores of the background class, but this will be ignored.
        score_thr (float): bbox threshold, bboxes with scores lower than it
            will not be considered.
        nms_thr (float): NMS IoU threshold
        max_num (int, optional): if there are more than max_num bboxes after
            NMS, only top max_num will be kept. Default to -1.
        score_factors (Tensor, optional): The factors multiplied to scores
            before applying NMS. Default to None.
        return_inds (bool, optional): Whether return the indices of kept
            bboxes. Default to False.

    Returns:
        tuple: (bboxes, labels, indices (optional)), tensors of shape (k, 5),
            (k), and (k). Labels are 0-based.
    """
    # pdb.set_trace()
    dets, labels = multiclass_nms_npu(multi_bboxes, multi_scores, score_thr, nms_cfg, max_num, score_factors, return_inds)
    return dets, labels
# def multiclass_nms(multi_bboxes,
#                    multi_scores,
#                    score_thr,
#                    nms_cfg,
#                    max_num=-1,
#                    score_factors=None):
#     """NMS for multi-class bboxes.
#
#     Args:
#         multi_bboxes (Tensor): shape (n, #class*4) or (n, 4)
#         multi_scores (Tensor): shape (n, #class), where the last column
#             contains scores of the background class, but this will be ignored.
#         score_thr (float): bbox threshold, bboxes with scores lower than it
#             will not be considered.
#         nms_thr (float): NMS IoU threshold
#         max_num (int): if there are more than max_num bboxes after NMS,
#             only top max_num will be kept.
#         score_factors (Tensor): The factors multiplied to scores before
#             applying NMS
#
#     Returns:
#         tuple: (bboxes, labels), tensors of shape (k, 5) and (k, 1). Labels \
#             are 0-based.
#     """
#     num_classes = multi_scores.size(1) - 1
#     # exclude background category
#     if multi_bboxes.shape[1] > 4:
#         bboxes = multi_bboxes.view(multi_scores.size(0), -1, 4)
#     else:
#         bboxes = multi_bboxes[:, None].expand(
#             multi_scores.size(0), num_classes, 4)
#     scores = multi_scores[:, :-1]
#
#     # filter out boxes with low scores
#     valid_mask = scores > score_thr
#
#     # We use masked_select for ONNX exporting purpose,
#     # which is equivalent to bboxes = bboxes[valid_mask]
#     # (TODO): as ONNX does not support repeat now,
#     # we have to use this ugly code
#     bboxes = torch.masked_select(
#         bboxes,
#         torch.stack((valid_mask, valid_mask, valid_mask, valid_mask),
#                     -1)).view(-1, 4)
#     if score_factors is not None:
#         scores = scores * score_factors[:, None]
#     scores = torch.masked_select(scores, valid_mask)
#     labels = valid_mask.nonzero(as_tuple=False)[:, 1]
#
#     if bboxes.numel() == 0:
#         bboxes = multi_bboxes.new_zeros((0, 5))
#         labels = multi_bboxes.new_zeros((0, ), dtype=torch.long)
#
#         if torch.onnx.is_in_onnx_export():
#             raise RuntimeError('[ONNX Error] Can not record NMS '
#                                'as it has not been executed this time')
#         return bboxes, labels
#
#     dets, keep = batched_nms(bboxes, scores.float(), labels, nms_cfg)
#
#     if max_num > 0:
#         dets = dets[:max_num]
#         keep = keep[:max_num]
#
#     return dets, labels[keep]


def fast_nms(multi_bboxes,
             multi_scores,
             multi_coeffs,
             score_thr,
             iou_thr,
             top_k,
             max_num=-1):
    """Fast NMS in `YOLACT <https://arxiv.org/abs/1904.02689>`_.

    Fast NMS allows already-removed detections to suppress other detections so
    that every instance can be decided to be kept or discarded in parallel,
    which is not possible in traditional NMS. This relaxation allows us to
    implement Fast NMS entirely in standard GPU-accelerated matrix operations.

    Args:
        multi_bboxes (Tensor): shape (n, #class*4) or (n, 4)
        multi_scores (Tensor): shape (n, #class+1), where the last column
            contains scores of the background class, but this will be ignored.
        multi_coeffs (Tensor): shape (n, #class*coeffs_dim).
        score_thr (float): bbox threshold, bboxes with scores lower than it
            will not be considered.
        iou_thr (float): IoU threshold to be considered as conflicted.
        top_k (int): if there are more than top_k bboxes before NMS,
            only top top_k will be kept.
        max_num (int): if there are more than max_num bboxes after NMS,
            only top max_num will be kept. If -1, keep all the bboxes.
            Default: -1.

    Returns:
        tuple: (bboxes, labels, coefficients), tensors of shape (k, 5), (k, 1),
            and (k, coeffs_dim). Labels are 0-based.
    """

    scores = multi_scores[:, :-1].t()  # [#class, n]
    scores, idx = scores.sort(1, descending=True)

    idx = idx[:, :top_k].contiguous()
    scores = scores[:, :top_k]  # [#class, topk]
    num_classes, num_dets = idx.size()
    boxes = multi_bboxes[idx.view(-1), :].view(num_classes, num_dets, 4)
    coeffs = multi_coeffs[idx.view(-1), :].view(num_classes, num_dets, -1)

    iou = bbox_overlaps(boxes, boxes)  # [#class, topk, topk]
    iou.triu_(diagonal=1)
    iou_max, _ = iou.max(dim=1)

    # Now just filter out the ones higher than the threshold
    keep = iou_max <= iou_thr

    # Second thresholding introduces 0.2 mAP gain at negligible time cost
    keep *= scores > score_thr

    # Assign each kept detection to its corresponding class
    classes = torch.arange(
        num_classes, device=boxes.device)[:, None].expand_as(keep)
    classes = classes[keep]

    boxes = boxes[keep]
    coeffs = coeffs[keep]
    scores = scores[keep]

    # Only keep the top max_num highest scores across all classes
    scores, idx = scores.sort(0, descending=True)
    if max_num > 0:
        idx = idx[:max_num]
        scores = scores[:max_num]

    classes = classes[idx]
    boxes = boxes[idx]
    coeffs = coeffs[idx]

    cls_dets = torch.cat([boxes, scores[:, None]], dim=1)
    return cls_dets, classes, coeffs