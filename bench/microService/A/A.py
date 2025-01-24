from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

DATA_DIR = "/home/data/"
B_URL = "http://kube-bench-server-service:15016"  # B 서비스의 주소와 포트

@app.route('/A', methods=['POST'])
def trigger_file_transfer():
    # 사용자의 요청을 확인
    trigger = request.form['trigger']  
    
    if trigger != "A" and trigger != "B":
        return "Invalid trigger.", 400

    # B에게 1MB 파일을 전송하는 요청을 보냄
    file_path = os.path.join(DATA_DIR, "1MB_file.dat")
    if not os.path.exists(file_path):
        return "1MB file not found.", 404

    print('check1')
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'application/octet-stream')}
        print('check2')
        response = requests.post(f"{B_URL}/receive-file", files=files)
        print('check3')
        if response.status_code == 200:
            return jsonify({"status": "File transfer initiated to B"})
        else:
            return jsonify({"status": "Failed to initiate file transfer to B"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=15015)
