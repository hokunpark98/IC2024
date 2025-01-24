#!/bin/bash

kubectl create -f /home/dnclab/hokun/kube/code/scheduler/bench/service2_hokun.yaml
kubectl create -f /home/dnclab/hokun/kube/code/scheduler/bench/service2_apple.yaml
kubectl create -f /home/dnclab/hokun/kube/code/scheduler/bench/service4_banana.yaml
kubectl create -f /home/dnclab/hokun/kube/code/scheduler/bench/service7_cherry.yaml

