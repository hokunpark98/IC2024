#!/bin/bash

# 시작 시간 기록 (밀리초 단위)
start_time=$(date +%s%3N)

# 예를 들어, productpage 서비스에 요청을 보냅니다.
kubectl exec "$(kubectl get pod -n apple -l app=productpage -o jsonpath='{.items[0].metadata.name}')" -c istio-proxy -- curl -sS http://reviews:9080/reviews/0

# 종료 시간 기록 (밀리초 단위)
end_time=$(date +%s%3N)

# 총 소요 시간 계산
duration=$((end_time - start_time))

echo "Total time taken: ${duration} milliseconds"
