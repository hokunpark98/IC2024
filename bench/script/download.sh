#!/bin/sh
FILE_SIZE=1MB
SLEEP_TIME=10

for i in 0 1 2 3 4 5 6 7 8 9
do 
    for j in 1 2
    do  
        echo "실험 횟수: $(($j + $i * 2))"
        
        kubectl exec kube-bench-client$j -n hokun -i  -- python3 /home/client.py $FILE_SIZE &

        sleep $SLEEP_TIME
    done
done

echo "결과 전송"
for i in 1 2 3 4 5
do 
expect << EOF
spawn kubectl exec kube-bench-client$i -n hokun -it -- scp -P 8023 /home/result.txt dnclab@163.152.30.135:/home/dnclab/hokun/kube/bench/result/client$i-$FILE_SIZE.txt

expect {
    "Are you sure you want to continue connecting" {
        send "yes\r"
        expect "dnclab@163.152.30.135's password" { send "dnclab\r" }
    }
    "dnclab@163.152.30.135's password" { send "dnclab\r" }
}
expect eof
EOF
sleep 1
done

echo "삭제"
for i in 1 2 3 4 5
do 
kubectl exec kube-bench-client$i -n hokun -it -- rm -rf /home/result.txt
sleep 0.5
done





