#!/bin/bash

python3 /home/dnclab/hokun/kube/code/scheduler/placement.py /home/dnclab/hokun/kube/code/scheduler/bench/service2_hokun.yaml
python3 /home/dnclab/hokun/kube/code/scheduler/placement.py /home/dnclab/hokun/kube/code/scheduler/bench/service2_apple.yaml
python3 /home/dnclab/hokun/kube/code/scheduler/placement.py /home/dnclab/hokun/kube/code/scheduler/bench/service4_banana.yaml
python3 /home/dnclab/hokun/kube/code/scheduler/placement.py /home/dnclab/hokun/kube/code/scheduler/bench/service7_cherry.yaml

