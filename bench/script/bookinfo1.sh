# productpage 파드의 이름을 찾습니다.
PRODUCTPAGE_POD=$(kubectl get pod -l app=productpage -o jsonpath='{.items[0].metadata.name}')

# productpage 파드에서 reviews 서비스를 호출한 후 ratings 서비스를 호출합니다.
kubectl exec $PRODUCTPAGE_POD -c istio-proxy -- sh -c '
  echo "Calling reviews service from productpage...";
  curl -sS http://reviews:9080/reviews/0;

  echo "Simulating call to ratings service from reviews...";
  curl -sS http://ratings:9080/ratings/0;
'
