from prometheus_api_client import PrometheusConnect

# Prometheus 서버 URL 설정
prom_url = "http://localhost:9090"  # 여기에 Prometheus 서버의 URL을 입력하세요

# PrometheusConnect 객체 생성
prom = PrometheusConnect(url=prom_url, disable_ssl=True)

# 전송률 쿼리 실행
transmit_query = "sum(rate(node_network_transmit_bytes_total[5m]))"
transmit_data = prom.custom_query(query=transmit_query)

# 수신률 쿼리 실행
receive_query = "sum(rate(node_network_receive_bytes_total[5m]))"
receive_data = prom.custom_query(query=receive_query)

# 결과 출력
print("Transmit Data (in bytes per second):", transmit_data)
print("Receive Data (in bytes per second):", receive_data)
