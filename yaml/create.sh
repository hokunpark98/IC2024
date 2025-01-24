#!/bin/sh
kubectl create -f /home/dnclab/hokun/kube/yaml/matrix/8192/1.yaml &
kubectl create -f /home/dnclab/hokun/kube/yaml/matrix/8192/2.yaml &
kubectl create -f /home/dnclab/hokun/kube/yaml/matrix/8192/3.yaml &
kubectl create -f /home/dnclab/hokun/kube/yaml/matrix/8192/4.yaml
