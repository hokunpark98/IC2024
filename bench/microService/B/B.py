from flask import Flask, request
import requests
import os

app = Flask(__name__)

DATA_DIR = "/home/data/"  # 파일을 저장할 디렉토리
C_URL = "http://kube-bench-server-service:15017"  # C 서비스의 주소와 포트

@app.route('/B', methods=['POST'])
def receive_file():
    # 파일을 받음
    file = request.files['fileA']
    filename = file.filename

    if not filename:
        return "No file received.", 400

    # 파일을 저장
    file_path = os.path.join(DATA_DIR, filename)
    file.save(file_path)

    # 파일 수신 후 C에게 3MB 파일을 전송
    send_file_to_C("3MB")
    return f"File {filename} received and saved.", 200


def send_file_to_C(filesize):
    # C에게 파일을 전송하는 로직
    file_path = os.path.join(DATA_DIR, f"{filesize}_file.dat")
    if not os.path.exists(file_path):
        print(f"File {filesize} not found for sending to C.")
        return

    with open(file_path, 'rb') as f:
        files = {'fileB': (file_path, f, 'application/octet-stream')}
        response = requests.post(f"{C_URL}/receive-file", files=files)
        if response.status_code == 200:
            print(f"File {filesize} sent to C successfully.")
        else:
            print(f"Failed to send file {filesize} to C.")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=15016)  # B 서비스의 포트