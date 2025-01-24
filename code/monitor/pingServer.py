# 서버 코드
import socket
import json
import time
import threading
from flask import Flask, jsonify

class RTTCollector:
    def __init__(self):
        self.HOST = "192.168.0.3"
        self.PORT = 10050
        self.results = {}
        self.lock = threading.Lock()

        self.ip_to_worker = {
            '192.168.0.4': 'worker1',
            '192.168.0.5': 'worker2',
            '192.168.0.6': 'worker3'
        }

    def run(self):
        aggregated_results = {}
        end_time = time.time() + 5

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((self.HOST, self.PORT))

            while True:
                try:
                    data, addr = s.recvfrom(1024)
                    incoming_data = json.loads(data.decode('utf-8'))

                    for worker_ip, rtt_data in incoming_data.items():
                        worker_name = self.ip_to_worker[worker_ip]
                        for target_ip, rtt in rtt_data.items():
                            target_name = self.ip_to_worker[target_ip]
                            key = f"{worker_name}<->{target_name}"
                            if key in aggregated_results:
                                aggregated_results[key].append(rtt)
                            else:
                                aggregated_results[key] = [rtt]

                    if time.time() > end_time:
                        new_results = {}
                        for key, values in aggregated_results.items():
                            avg_rtt = sum(values) / len(values)
                            new_results[key] = round(avg_rtt * 1000, 3)

                        with self.lock:
                            self.results = new_results

                        aggregated_results = {}
                        end_time = time.time() + 5

                except Exception as e:
                    print(f"An error occurred: {e}")

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()


    def get(self):
        with self.lock:
            return self.results.copy()

if __name__ == "__main__":
    app = Flask(__name__)

    # RTTCollector 인스턴스 생성
    collector = RTTCollector()
    collector.start()

    # RTT 데이터를 반환하는 라우트
    @app.route('/get_rtt', methods=['GET'])
    def get_rtt():
        return jsonify(collector.get())

    if __name__ == "__main__":
        # Flask 애플리케이션을 5000번 포트에서 실행
        app.run(host='0.0.0.0', port=5000)
   



