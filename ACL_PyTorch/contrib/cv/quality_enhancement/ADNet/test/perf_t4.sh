#!/bin/bash

# T4���ܲ���
rm -rf perf1.log
trtexec --onnx=ADNet.onnx --fp16 --shapes=image:1x1x321x481 --threads > perf1.log
perf_str=`grep "GPU.* mean.*ms$" perf1.log`
if [ -n "$perf_str" ]; then
    perf_num=`echo $perf_str | awk -F' ' '{print $16}'`
else
    perf_str=`grep "mean.*ms$" perf1.log`
    perf_num=`echo $perf_str | awk -F' ' '{print $4}'`
fi
awk 'BEGIN{printf "t4 bs1 fps:%.3f\n", 1000*1/('$perf_num'/1)}'


rm -rf perf4.log
trtexec --onnx=ADNet.onnx --fp16 --shapes=image:4x1x321x481 --threads > perf4.log
perf_str=`grep "GPU.* mean.*ms$" perf4.log`
if [ -n "$perf_str" ]; then
    perf_num=`echo $perf_str | awk -F' ' '{print $16}'`
else
    perf_str=`grep "mean.*ms$" perf4.log`
    perf_num=`echo $perf_str | awk -F' ' '{print $4}'`
fi
awk 'BEGIN{printf "t4 bs4 fps:%.3f\n", 1000*1/('$perf_num'/4)}'


rm -rf perf8.log
trtexec --onnx=ADNet.onnx --fp16 --shapes=image:8x1x321x481 --threads > perf8.log
perf_str=`grep "GPU.* mean.*ms$" perf8.log`
if [ -n "$perf_str" ]; then
    perf_num=`echo $perf_str | awk -F' ' '{print $16}'`
else
    perf_str=`grep "mean.*ms$" perf8.log`
    perf_num=`echo $perf_str | awk -F' ' '{print $4}'`
fi
awk 'BEGIN{printf "t4 bs8 fps:%.3f\n", 1000*1/('$perf_num'/8)}'


rm -rf perf16.log
trtexec --onnx=ADNet.onnx --fp16 --shapes=image:16x1x321x481 --threads > perf16.log
perf_str=`grep "GPU.* mean.*ms$" perf16.log`
if [ -n "$perf_str" ]; then
    perf_num=`echo $perf_str | awk -F' ' '{print $16}'`
else
    perf_str=`grep "mean.*ms$" perf16.log`
    perf_num=`echo $perf_str | awk -F' ' '{print $4}'`
fi
awk 'BEGIN{printf "t4 bs16 fps:%.3f\n", 1000*1/('$perf_num'/16)}'


rm -rf perf32.log
trtexec --onnx=ADNet.onnx --fp16 --shapes=image:32x1x321x481 --threads > perf32.log
perf_str=`grep "GPU.* mean.*ms$" perf32.log`
if [ -n "$perf_str" ]; then
    perf_num=`echo $perf_str | awk -F' ' '{print $16}'`
else
    perf_str=`grep "mean.*ms$" perf32.log`
    perf_num=`echo $perf_str | awk -F' ' '{print $4}'`
fi
awk 'BEGIN{printf "t4 bs32 fps:%.3f\n", 1000*1/('$perf_num'/32)}'
