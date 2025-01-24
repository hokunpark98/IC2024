#!/bin/sh
SLEEP_TIME1=2
SLEEP_TIME2=5
echo "시작"

for i in 0 1 2 3 4 5 6 7 8 9
do 
    echo "$i번 실행"
    kubectl exec kube-bench-client1 -n hokun -i  -- python3 /home/client.py 1KB &
    sleep $SLEEP_TIME1
    kubectl exec kube-bench-client1 -n apple -i  -- python3 /home/client.py 5MB &
    sleep $SLEEP_TIME1
    kubectl exec kube-bench-client1 -n banana -i  -- python3 /home/client.py 1KB &
    sleep $SLEEP_TIME1
    kubectl exec kube-bench-client2 -n banana -i  -- python3 /home/client.py 1MB &
    sleep $SLEEP_TIME1
    kubectl exec kube-bench-client3 -n banana -i  -- python3 /home/client.py 1KB &
    sleep $SLEEP_TIME1
    kubectl exec kube-bench-client1 -n cherry -i  -- python3 /home/client.py 500KB &
    sleep $SLEEP_TIME1
    kubectl exec kube-bench-client2 -n cherry -i  -- python3 /home/client.py 1MB &
    sleep $SLEEP_TIME1
    kubectl exec kube-bench-client3 -n cherry -i  -- python3 /home/client.py 1KB &
    sleep $SLEEP_TIME1
    kubectl exec kube-bench-client4 -n cherry -i  -- python3 /home/client.py 5MB &
    sleep $SLEEP_TIME2
    kubectl exec kube-bench-client5 -n cherry -i  -- python3 /home/client.py 5MB &
    sleep $SLEEP_TIME2
    kubectl exec kube-bench-client6 -n cherry -i  -- python3 /home/client.py 1MB &
    sleep $SLEEP_TIME2
    
done

echo "결과 전송"
expect << EOF
spawn kubectl exec kube-bench-client1 -n hokun -it -- scp -P 8023 /home/result.txt dnclab@163.152.30.135:/home/dnclab/hokun/kube/bench/result/hokun1.txt

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

expect << EOF
spawn kubectl exec kube-bench-client1 -n apple -it -- scp -P 8023 /home/result.txt dnclab@163.152.30.135:/home/dnclab/hokun/kube/bench/result/apple1.txt

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
expect << EOF
spawn kubectl exec kube-bench-client1 -n banana -it -- scp -P 8023 /home/result.txt dnclab@163.152.30.135:/home/dnclab/hokun/kube/bench/result/banana1.txt

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
expect << EOF
spawn kubectl exec kube-bench-client2 -n banana -it -- scp -P 8023 /home/result.txt dnclab@163.152.30.135:/home/dnclab/hokun/kube/bench/result/banana2.txt

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
expect << EOF
spawn kubectl exec kube-bench-client3 -n banana -it -- scp -P 8023 /home/result.txt dnclab@163.152.30.135:/home/dnclab/hokun/kube/bench/result/banana3.txt

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
expect << EOF
spawn kubectl exec kube-bench-client1 -n cherry -it -- scp -P 8023 /home/result.txt dnclab@163.152.30.135:/home/dnclab/hokun/kube/bench/result/cherry1.txt

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
expect << EOF
spawn kubectl exec kube-bench-client2 -n cherry -it -- scp -P 8023 /home/result.txt dnclab@163.152.30.135:/home/dnclab/hokun/kube/bench/result/cherry2.txt

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
expect << EOF
spawn kubectl exec kube-bench-client3 -n cherry -it -- scp -P 8023 /home/result.txt dnclab@163.152.30.135:/home/dnclab/hokun/kube/bench/result/cherry3.txt

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
expect << EOF
spawn kubectl exec kube-bench-client4 -n cherry -it -- scp -P 8023 /home/result.txt dnclab@163.152.30.135:/home/dnclab/hokun/kube/bench/result/cherry4.txt

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
expect << EOF
spawn kubectl exec kube-bench-client5 -n cherry -it -- scp -P 8023 /home/result.txt dnclab@163.152.30.135:/home/dnclab/hokun/kube/bench/result/cherry5.txt

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
expect << EOF
spawn kubectl exec kube-bench-client6 -n cherry -it -- scp -P 8023 /home/result.txt dnclab@163.152.30.135:/home/dnclab/hokun/kube/bench/result/cherry6.txt

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
kubectl exec kube-bench-client1 -n hokun -i  -- rm -rf /home/result.txt
kubectl exec kube-bench-client1 -n apple -i  -- rm -rf /home/result.txt
kubectl exec kube-bench-client1 -n banana -i  -- rm -rf /home/result.txt
kubectl exec kube-bench-client2 -n banana -i  -- rm -rf /home/result.txt
kubectl exec kube-bench-client3 -n banana -i  -- rm -rf /home/result.txt
kubectl exec kube-bench-client1 -n cherry -i  -- rm -rf /home/result.txt
kubectl exec kube-bench-client2 -n cherry -i  -- rm -rf /home/result.txt
kubectl exec kube-bench-client3 -n cherry -i  -- rm -rf /home/result.txt
kubectl exec kube-bench-client4 -n cherry -i  -- rm -rf /home/result.txt
kubectl exec kube-bench-client5 -n cherry -i  -- rm -rf /home/result.txt
kubectl exec kube-bench-client6 -n cherry -i  -- rm -rf /home/result.txt
sleep 3

echo "종료"



