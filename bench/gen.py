import random

MB = 1024 * 1024
KB = 1024

def create_file_with_size(file_name, size):
    with open(file_name, 'wb') as f:
        for _ in range(size):  # 1 MB = 1024 * 1024 bytes
            f.write(bytes([random.randint(0, 9)]))


create_file_with_size('/home/dnclab/hokun/kube/bench/server/data/1Byte_file.dat', 1)
create_file_with_size('/home/dnclab/hokun/kube/bench/server/data/1KB_file.dat', 1 * KB)
create_file_with_size('/home/dnclab/hokun/kube/bench/server/data/500KB_file.dat', 500 * KB)
create_file_with_size('/home/dnclab/hokun/kube/bench/server/data/1MB_file.dat', 1 * MB)
create_file_with_size('/home/dnclab/hokun/kube/bench/server/data/3MB_file.dat', 3 * MB)
create_file_with_size('/home/dnclab/hokun/kube/bench/server/data/5MB_file.dat', 5 * MB)
create_file_with_size('/home/dnclab/hokun/kube/bench/server/data/10MB_file.dat', 10 * MB)
