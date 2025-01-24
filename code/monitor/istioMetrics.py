import requests


class IstioMetrics:
    def __init__(self):
        self.prometheus_url = "http://localhost:9090"
        self.traffic_map = {}
        self.latency_dict = {'worker1-worker2': 0.01, 'worker1-worker3': 0.001, 'worker2-worker3': 0.001,
                     'worker2-worker1': 0.01, 'worker3-worker1': 0.001, 'worker3-worker2': 0.001}

    def generate_key(self, source, dest):
        return f"{source} <-> {dest}" if source < dest else f"{dest} <-> {source}"

    def fetch_metric(self, query):
        response = requests.get(f"{self.prometheus_url}/api/v1/query", params={"query": query})

        if response.status_code != 200:
            print(f"Error fetching metrics: {response.text}")
            return {}

        data = response.json()
        result_map = {}

        for result in data['data']['result']:
            source = result['metric']['source_workload']
            dest = result['metric']['destination_workload']
            if source == 'unknown' or dest == 'unknown':
                continue
            total_bytes_str = result['value'][1]

            try:
                total_bytes = float(total_bytes_str)
            except ValueError as e:
                print(f"Error converting bytes value to float: {e}")
                continue

            key = self.generate_key(source, dest)
            result_map[key] = total_bytes

        return result_map

    def fetch_metrics(self):
        request_metrics = self.fetch_metric(self.request_query)
        response_metrics = self.fetch_metric(self.response_query)
        count_metrics = self.fetch_metric(self.count_query)

        for key, value in request_metrics.items():
            self.traffic_map[key] = self.traffic_map.get(key, 0) + value

        for key, value in response_metrics.items():
            self.traffic_map[key] = self.traffic_map.get(key, 0) + value

    def display_metrics(self):
        for key, value in self.traffic_map.items():
            print(f"{key}, {value:.2f} bytes/s")  # rate is usually expressed in bytes per second

    def get(self, namespace):
        self.request_query = f'istio_request_bytes_sum{{namespace="{namespace}"}}'
        self.response_query = f'istio_response_bytes_sum{{namespace="{namespace}"}}'
        self.count_query = f'istio_requests_total{{namespace="{namespace}"}}'
        
        self.fetch_metrics()
        return self.traffic_map


if __name__ == "__main__":
    prom = IstioMetrics()
    result = prom.get('default')
    print(result)
