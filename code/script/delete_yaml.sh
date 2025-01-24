#!/bin/bash

kubectl delete -f /home/dnclab/hokun/kube/code/scheduler/bench/service2_hokun.yaml
kubectl delete -f /home/dnclab/hokun/kube/code/scheduler/bench/service2_apple.yaml
kubectl delete -f /home/dnclab/hokun/kube/code/scheduler/bench/service4_banana.yaml
kubectl delete -f /home/dnclab/hokun/kube/code/scheduler/bench/service7_cherry.yaml

