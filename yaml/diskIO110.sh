#!/bin/sh
kubectl create -f /home/dnclab/hokun/kube/yaml/diskIO/110/1.yaml
kubectl create -f /home/dnclab/hokun/kube/yaml/diskIO/110/2.yaml
kubectl create -f /home/dnclab/hokun/kube/yaml/diskIO/110/3.yaml
kubectl create -f /home/dnclab/hokun/kube/yaml/diskIO/110/4.yaml
kubectl create -f /home/dnclab/hokun/kube/yaml/diskIO/110/5.yaml
kubectl create -f /home/dnclab/hokun/kube/yaml/diskIO/110/6.yaml
kubectl create -f /home/dnclab/hokun/kube/yaml/diskIO/110/7.yaml
kubectl create -f /home/dnclab/hokun/kube/yaml/diskIO/110/8.yaml
kubectl create -f /home/dnclab/hokun/kube/yaml/diskIO/110/9.yaml
kubectl create -f /home/dnclab/hokun/kube/yaml/diskIO/110/10.yaml
kubectl create -f /home/dnclab/hokun/kube/yaml/diskIO/110/11.yaml
kubectl create -f /home/dnclab/hokun/kube/yaml/diskIO/110/12.yaml

sleep 15
kubectl get pods -o wide