#!/bin/bash

onnx=$1
om=$2
bs=$3
soc_version=$4

atc --model=${onnx}.onnx \
    --output=${om} \
    --input_shape="input:${bs},64600" \
    --log=error \
    --framework=5 \
    --soc_version=${soc_version} \
    --input_format=ND \
    --optypelist_for_implmode="Sigmoid" \
    --op_select_implmode=high_performance

