#!/bin/sh
kubectl create -f /home/kube/yaml/diskIO/150/1.yaml
kubectl create -f /home/kube/yaml/diskIO/150/2.yaml
kubectl create -f /home/kube/yaml/diskIO/150/3.yaml
#kubectl create -f /home/kube/yaml/diskIO/150/4.yaml
#kubectl create -f /home/kube/yaml/diskIO/150/5.yaml
#kubectl create -f /home/kube/yaml/diskIO/150/6.yaml
#kubectl create -f /home/kube/yaml/diskIO/150/7.yaml

sleep 15
kubectl get pods -o wide