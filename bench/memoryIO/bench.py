import os
import time
from multiprocessing import Process

def memory_intensive_task():
    bytes_in_gib = 10 * (1024 ** 3)
    memory_block = bytearray(bytes_in_gib)

    while True:
        position = os.urandom(1)[0] % bytes_in_gib
        memory_block[position] = os.urandom(1)[0]

# 병렬로 실행할 프로세스의 수
process_count = 4

processes = []

for _ in range(process_count):
    process = Process(target=memory_intensive_task)
    process.start()
    processes.append(process)

# 모든 프로세스가 완료될 때까지 기다림
for process in processes:
    process.join()
