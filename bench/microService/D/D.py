from flask import Flask, request
import os

app = Flask(__name__)

DATA_DIR = "/home/data"  # 파일을 저장할 디렉토리

@app.route('/D', methods=['POST'])
def receive_file():
    # 파일을 받음
    file = request.files['fileC']
    filename = file.filename

    if not filename:
        return "No file received.", 400

    # 파일을 저장
    file_path = os.path.join(DATA_DIR, filename)
    file.save(file_path)

    print(f"File {filename} received and saved successfully")

    return f"File {filename} received and saved.", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=15018)  # D 서비스의 포트