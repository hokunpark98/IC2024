from flask import Flask, request, send_from_directory
import os

app = Flask(__name__)

DATA_DIR = "/home/data"

@app.route('/<filesize>', methods=['GET'])
def send_file(filesize):
    
    if filesize not in ['1Byte', '1KB', '500KB', '1MB', '3MB', '5MB', '10MB']:
        return "Invalid filesize received.", 400

    filename = f"{filesize}_file.dat"
    file_path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(file_path):
        return "File not found.", 404

    return send_from_directory(DATA_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=15015)
