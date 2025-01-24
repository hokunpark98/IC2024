import requests
import networkx as nx
import matplotlib.pyplot as plt
from kubernetes import client, config
from collections import defaultdict

class IstioMetricsDict:
    def __init__(self):
        self.prometheus_url = "http://localhost:9090"
        

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
            value_str = result['value'][1]

            try:
                value = float(value_str)
            except ValueError as e:
                print(f"Error converting value to float: {e}")
                continue

            if source not in result_map:
                result_map[source] = {}
            if dest not in result_map[source]:
                result_map[source][dest] = [0, 0]  

            result_map[source][dest][1] += value

        return result_map

    def fetch_metrics(self):
        traffic_map = {}
        request_metrics = self.fetch_metric(self.request_query)
        response_metrics = self.fetch_metric(self.response_query)
        count_metrics = self.fetch_metric(self.count_query)


        for source, destinations in count_metrics.items():
            for dest, count in destinations.items():
                if source in request_metrics and dest in request_metrics[source]:
                    traffic_map[source] = traffic_map.get(source, {})
                    total_bytes = request_metrics[source][dest][1] + response_metrics.get(source, {}).get(dest, [0, 0])[1] / 2
                    total_Mbytes = round(total_bytes / (1024 * 1024) , 2)
                    traffic_map[source][dest] = [count[1], total_Mbytes]
        return traffic_map


    def get(self, namespace):
        self.request_query = f'istio_request_bytes_sum{{namespace="{namespace}"}}'
        self.response_query = f'istio_response_bytes_sum{{namespace="{namespace}"}}'
        self.count_query = f'istio_requests_total{{namespace="{namespace}"}}'
        
        return self.fetch_metrics()
   



    def fetch_pods_on_node(self, node_name):
        config.load_kube_config()
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node_name}")
        return [pod.metadata.name for pod in pods.items]



    def calculate_node_traffic(self, node_name, traffic_map):
        pod_names = self.fetch_pods_on_node(node_name)
        node_traffic_total = defaultdict(float)

        for source, destinations in traffic_map.items():
            if source in pod_names:
                for dest, data in destinations.items():
                    node_traffic_total[source] += data[1]
                    if dest in pod_names:
                        node_traffic_total[dest] += data[1]

        sorted_traffic = sorted(node_traffic_total.items(), key=lambda x: x[1])
        return dict(sorted_traffic)


    def fetch_pods_on_node(self, node_name, namespace):
        config.load_kube_config()
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node_name}").items

        # Filter pods by the specified namespace
        return [pod.metadata.name for pod in pods if pod.metadata.namespace == namespace]

    def calculate_node_traffic(self, node_name, traffic_map, namespace):
        pod_names = self.fetch_pods_on_node(node_name, namespace)
        node_traffic_total = {pod: 0 for pod in pod_names}  # Initialize all traffic to 0

        # Accumulate traffic data from the traffic_map
        for source, destinations in traffic_map.items():
            if source in node_traffic_total:
                for dest, data in destinations.items():
                    node_traffic_total[source] += data[1]  # Add traffic to source pod
                    if dest in node_traffic_total:
                        node_traffic_total[dest] += data[1]  # Add traffic to destination pod

        sorted_traffic = sorted(node_traffic_total.items(), key=lambda x: x[1])
        return dict(sorted_traffic)


    
# 사용 예시
if __name__ == "__main__":
    prom = IstioMetricsDict()
    traffic_map = prom.get('hokun')

    node_name = input("Enter node name: ")
    node_traffic = prom.calculate_node_traffic(node_name, traffic_map)
    print(f"Total traffic per pod for node '{node_name}':")
    for pod, traffic in node_traffic.items():
        print(f"{pod}: {traffic} MB")
