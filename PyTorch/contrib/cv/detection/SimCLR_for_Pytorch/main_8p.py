"""MIT License"""
# Copyright (c) 2020 Thalles Silva
# Copyright 2021 Huawei Technologies Co., Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ============================================================================
import os
import time
import argparse
import torch
if torch.__version__ >= "1.8":
    import torch_npu
import torch.npu
import torch.nn.functional as F
import torch.multiprocessing as mp
import torch.backends.cudnn as cudnn
from torchvision import models
from utils import accuracy
from models.resnet_simclr import ResNetSimCLR

from apex import amp
from data_aug.contrastive_learning_dataset import ContrastiveLearningDataset
from multi_epochs_dataloader import MultiEpochsDataLoader
import apex
from apex.optimizers import NpuFusedAdam
import socket

torch.manual_seed(0)

model_names = sorted(name for name in models.__dict__
                     if name.islower() and not name.startswith("__")
                     and callable(models.__dict__[name]))

parser = argparse.ArgumentParser(description='PyTorch SimCLR')
parser.add_argument('data', metavar='DIR',
                    help='path to dataset')
parser.add_argument('--dataset_name', default='cifar10',
                    help='dataset name', choices=['stl10', 'cifar10'])
parser.add_argument('-a', '--arch', metavar='ARCH', default='resnet18',
                    choices=model_names,
                    help='model architecture: ' +
                         ' | '.join(model_names) +
                         ' (default: resnet50)')
parser.add_argument('-j', '--workers', default=9, type=int, metavar='N',
                    help='number of data loading workers (default: 9)')
parser.add_argument('--epochs', default=100, type=int, metavar='N',
                    help='number of total epochs to run')
parser.add_argument('-b', '--batch_size', default=256, type=int,
                    metavar='N',
                    help='mini-batch size (default: 256), this is the total '
                         'batch size of all GPUs on the current node when '
                         'using Data Parallel or Distributed Data Parallel')
parser.add_argument('--lr', '--learning_rate', default=0.0012, type=float,
                    metavar='LR', help='initial learning rate', dest='lr')
parser.add_argument('--wd', '--weight_decay', default=1e-4, type=float,
                    metavar='W', help='weight decay (default: 1e-4)',
                    dest='weight_decay')
parser.add_argument('--out_dim', default=128, type=int,
                    help='feature dimension (default: 128)')
parser.add_argument('--log_every_n_steps', default=10, type=int,
                    help='Log every n steps')
parser.add_argument('--temperature', default=0.07, type=float,
                    help='softmax temperature (default: 0.07)')
parser.add_argument('--n_views', default=2, type=int, metavar='N',
                    help='Number of views for contrastive learning training.')
parser.add_argument('--rank', default=0, type=int,
                    help='node rank for distributed training')
parser.add_argument('--npu', default=0, type=int,
                    help='NPU id to use.')
parser.add_argument('--pretrained', dest='pretrained', action='store_true',
                    help='use pre-trained model')
parser.add_argument('--pth_path', default='', type=str, metavar='PATH',
                    help='path to pretrained checkpoint (default: none)')
parser.add_argument('--distributed', action='store_true',
                    help='Use multi-processing distributed training to launch '
                    'N processes per node, which has N GPUs.')
parser.add_argument('--nodes', type=int, default=1)
parser.add_argument('--device_id', type=int, default=0, help="device id")
parser.add_argument('--device_list', type=str, default="0,1,2,3,4,5,6,7", help="device id list")
parser.add_argument('--opt_level', type=str, default="O2", help="opt level")



def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def device_id_to_process_device_map(device_list):
    devices = device_list.split(",")
    devices = [int(x) for x in devices]
    devices.sort()

    process_device_map = dict()
    for process_id, device_id in enumerate(devices):
        process_device_map[process_id] = device_id

    return process_device_map


def main():
    print('Part1 : prepare for parameters <==> Begin')
    args = parser.parse_args()
    os.environ["MASTER_ADDR"] = get_host_ip()
    os.environ["MASTER_PORT"] = "29688"
    args.process_device_map = device_id_to_process_device_map(args.device_list)
    if args.device_list != '':
        npus_per_node = len(args.device_list.split(','))
    elif args.device_num != -1:
        npus_per_node = args.device_num
    elif args.device == 'npu':
        npus_per_node = torch.npu.device_count()
    else:
        npus_per_node = torch.cuda.device_count()

    print('npus_per_node:', npus_per_node)

    if args.distributed:
        mp.spawn(main_worker, nprocs=npus_per_node, args=(npus_per_node, args))
    else:
        # Simply call main_worker function
        main_worker(args.npu, npus_per_node, args)


def main_worker(npu, npus_per_node, args):
    local_rank = 0
    args.npu = args.process_device_map[npu]
    if args.distributed:
        args.rank = args.rank * npus_per_node + npu
        torch.distributed.init_process_group(backend="hccl",
                                             world_size=args.nodes * npus_per_node,
                                             rank=args.rank)
        local_rank = torch.distributed.get_rank()
    args.is_master_node = not args.distributed or local_rank == 0
    if args.is_master_node:
        print(args)
    args.device_id = args.device_id + local_rank
    print("device_id = ", args.device_id)
    device = torch.device(f'npu:{args.device_id}')
    torch.npu.set_device(device)

    # create model
    if args.pretrained:
        print("=> using pre-trained model ResNetSimCLR")
        model = ResNetSimCLR(base_model=args.arch, out_dim=args.out_dim)
        print("loading model of yours...")
        if args.pth_path:
            print("load pth you give")
            pretrained_dict = torch.load(args.pth_path, map_location="cpu")["state_dict"]
        else:
            pretrained_dict = torch.load("./checkpoint.pth.tar", map_location="cpu")["state_dict"]
        model.load_state_dict(pretrained_dict, strict=False)
    else:
        print("=> creating model ResNetSimCLR")
        model = ResNetSimCLR(base_model=args.arch, out_dim=args.out_dim)

    print('rank', args.rank, ' using npu...')
    if args.rank % npus_per_node == 0:
        print('Part1 : prepare for parameters <==> Done')
        print('Part2 : Load Network  <==> Begin')

    cudnn.deterministic = True
    cudnn.benchmark = True
    model = model.to(device)
    optimizer = NpuFusedAdam(
        model.parameters(),
        args.lr,
        weight_decay=args.weight_decay
    )
    model, optimizer = amp.initialize(model, optimizer, opt_level=args.opt_level, loss_scale="dynamic", combine_grad=True)
    if args.distributed:
        model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[local_rank],
                                                          broadcast_buffers=False)
    criterion = torch.nn.CrossEntropyLoss().to(device)

    if args.rank % npus_per_node == 0:
        print('Part2 : Load Network  <==> Done')
        print('Part3 : Load Dataset  <==> Begin')

    dataset = ContrastiveLearningDataset(args.data)
    train_dataset = dataset.get_dataset(args.dataset_name, args.n_views)
    print(f'workers nums:{args.workers}')
    print(f'device nums:{npus_per_node}')

    train_loader, train_loader_len, train_sampler = get_pytorch_train_loader(train_dataset,
                                                                             args.batch_size,
                                                                             workers=args.workers)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=len(train_loader), eta_min=0,
                                                           last_epoch=-1)
    if args.rank % npus_per_node == 0:
        print('Part3 : Load Dataset  <==> Done')
        print('Part4 : Train and Test  <==> Begin')

    best_acc = 0
    for epoch_counter in range(args.epochs):
        if args.distributed:
            train_sampler.set_epoch(epoch_counter)
        best_acc=train(args, train_loader, model, criterion, optimizer, epoch_counter, npus_per_node, best_acc)
        if epoch_counter >= 10:
            scheduler.step()
    print('Part4 : Train and Test  <==> Done')


def info_nce_loss(args, features):
    labels = torch.cat([torch.arange(args.batch_size) for i in range(args.n_views)], dim=0)
    labels = (labels.unsqueeze(0) == labels.unsqueeze(1)).float()
    labels = labels.npu()
    features = F.normalize(features, dim=1)
    similarity_matrix = torch.matmul(features, features.T)

    # discard the main diagonal from both: labels and similarities matrix
    mask = torch.eye(labels.shape[0], dtype=torch.bool).npu()
    labels = labels[~mask].view(labels.shape[0], -1)
    similarity_matrix = similarity_matrix[~mask].view(similarity_matrix.shape[0], -1)

    # select and combine multiple positives
    positives = similarity_matrix[labels.bool()].view(labels.shape[0], -1)

    # select only the negatives the negatives
    negatives = similarity_matrix[~labels.bool()].view(similarity_matrix.shape[0], -1)

    logits = torch.cat([positives, negatives], dim=1)
    labels = torch.zeros(logits.shape[0], dtype=torch.long).npu()
    logits = logits / args.temperature
    return logits, labels


def train(args, train_loader, model, criterion, optimizer, epoch_counter, npus_per_node, best_acc):
    fps = AverageMeter()

    top1 = [0]
    top5 = [0]

    end = time.time()
    for i, (images, _) in enumerate(train_loader):
        images = torch.cat(images, dim=0)
        images = images.npu()

        out = model(images)
        logits, labels = info_nce_loss(args, out)
        loss = criterion(logits, labels)
        optimizer.zero_grad()
        with amp.scale_loss(loss, optimizer) as scaled_loss:
            scaled_loss.backward()
        optimizer.step()

        time_step = time.time() - end
        fps.update(args.batch_size * npus_per_node / time_step)
        torch.npu.synchronize()
        end = time.time()

        if i % args.log_every_n_steps == 0 and args.is_master_node:
            top1, top5 = accuracy(logits, labels, topk=(1, 5))
            if top1[0] > best_acc:
                best_acc = top1[0]

            print('Train Epoch: {0} Step: {1}/{2} Loss {loss:.4f} Time {time:.4f}'
                  '[AVG-ACC] * Acc@1 {top1:.3f} Acc@5 {top5:.3f} best_acc {best_acc:.3f} '
                  'LR {lr:.7f} FPS {fps:.7f} '.format(
                    epoch_counter, i, len(train_loader), loss=loss.item(), time=time_step,
                    top1=top1[0], top5=top5[0], best_acc=best_acc,
                    lr=optimizer.param_groups[0]['lr'], fps=fps.avg))

    if (epoch_counter+1) % 5 == 0:
        save_checkpoint({
            'epoch': epoch_counter,
            'arch': model.state_dict(),
            'state_dict': model.state_dict(),
            'optimizer': optimizer.state_dict(),
        })

    return best_acc


def save_checkpoint(state, filename='checkpoint.pth.tar'):
    torch.save(state, filename)


def get_pytorch_train_loader(train_dataset, batch_size, workers, _worker_init_fn=None):
    train_sampler = torch.utils.data.distributed.DistributedSampler(train_dataset)

    dataloader_fn = MultiEpochsDataLoader  # torch.utils.data.DataLoader
    train_loader = dataloader_fn(
        train_dataset, batch_size=batch_size, shuffle=(train_sampler is None),
        num_workers=workers, worker_init_fn=_worker_init_fn, pin_memory=False, sampler=train_sampler,
        drop_last=True)
    return train_loader, len(train_loader), train_sampler


class AverageMeter(object):
    """Computes and stores the average and current value"""

    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


if __name__ == '__main__':
    main()
