import requests
import time
import os
import sys

URL = "http://kube-bench-server-service:15015"

def main(argv):
    filesize = argv[1]

    if os.path.exists("received_file.dat"):
        os.remove("received_file.dat")
    
    try:
        start_time = time.time_ns()
        response = requests.get(f"{URL}/{filesize}")
        end_time = time.time_ns()
        
        with open("received_file.dat", 'wb') as f:
            f.write(response.content)

        print("File received successfully")
        
        download_duration = end_time - start_time
        with open("result.txt", 'a') as f:
            f.write(str(download_duration) + '\n') 
        
    except Exception as e:
        print(f"Error occurred: {e}")
        

if __name__ == "__main__":
    main(sys.argv)
