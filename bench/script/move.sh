#!/bin/sh

FILE_SIZE=50

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





