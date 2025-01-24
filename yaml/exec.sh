#!/bin/sh
kubectl exec -i m-8192-1 -- /bin/bash -c python3 /home/main.py &
kubectl exec -i m-8192-2 -- /bin/bash -c python3 /home/main.py &
kubectl exec -i m-8192-3 -- /bin/bash -c python3 /home/main.py &
kubectl exec -i m-8192-4 -- python3 /home/main.py 
#kubectl exec -it m-8192-1 -- bash -c "python3 /home/main.py" &
#kubectl exec -it m-8192-1 -- bash -c "python3 /home/main.py" 
