#!/bin/sh

for i in 1 2 3 4 5 6
do 
kubectl exec kube-bench-client$i -n cherry -it -- rm -rf /home/result.txt
sleep 0.5
done



