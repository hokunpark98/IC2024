import time
from podResourceYAMLManager import PodResourceYAMLManager
from monitor.nodeMetrics import KubernetesInfo
from monitor.istioMetrics import IstioMetrics
from monitor.istioMetrics_dict import IstioMetricsDict
from monitor.pingServer import RTTCollector
import requests
import subprocess
import json


class Replacement:
    def __init__(self):
        self.node_info = KubernetesInfo()
        self.istio_info = IstioMetrics()
        self.istio_info_dict = IstioMetricsDict()
        self.podResourceYAMLManager = PodResourceYAMLManager()
        self.rtt_collector = RTTCollector()
        self.base_node_json = '/home/dnclab/hokun/kube/code/scheduler/base_node.json'
        self.namespaces = ['apple', 'banana', 'cherry', 'hokun']
        self.threshold = 30
    '''
    네임스페이스가 같은 파드명 수집
    istio에서 수집한 메트릭으로 함수 호출해서 파드명으로 어떤 파드와 통신하고 있는지 (한 번 통신시 얼마나 데이터를 전송하는지) 확인
    계산함수
    노드 자원 정하고 (R), 노드 간 지연 그냥 딕셔너리로 갖고 있기
    
    1. 네임스페이스가 같은 파드들 간의 통신량 확인
    2. 
    '''
    
    def get_network_latency_use_packet_size(self):
        all_pod_latency_in_namespace = {}
        for namespace in self.namespaces:
            temp = self.istio_info_dict.get(namespace)
            pod_latency_in_namespace = {}
            for source_pod in temp:
                for target_pod in temp[source_pod]:
                    print(source_pod)
                    latency = 0.001
                    source_pod_node = self.getNodeName(source_pod, namespace)
                    target_pod_node = self.getNodeName(target_pod, namespace)
                    if source_pod_node == 'master' or target_pod_node =='master':
                        continue 
                    if source_pod_node == target_pod_node: # 같은 노드에 있다면
                        latency = 0.001
                    else:
                        latency = self.istio_info.latency_dict[f'{source_pod_node}-{target_pod_node}']
                    
                    #temp[source_pod][target_pod]: [전송 횟수. 전송량]
                    send_count = temp[source_pod][target_pod][0]
                    data_size = round(temp[source_pod][target_pod][1] / temp[source_pod][target_pod][0], 1)
                    packet_count = int(data_size / self.packet_size)
                    if packet_count == 0:
                        packet_count = 1
                    
                    #총 네트워크 지연 시간
                    pod_latency = packet_count * latency * send_count
                    
                    #데이터사이즈/패킷사이즈 * 횟수 - 지연은 고려 안 한 값:
                    pod_send_packet_count = int(packet_count * send_count)
                    pod_latency_in_namespace[f'{source_pod}/{target_pod}'] = [pod_latency, pod_send_packet_count]
                    
        all_pod_latency_in_namespace[namespace] = pod_latency_in_namespace
        return all_pod_latency_in_namespace

   
    def getNodeName(self, pod_name, namespace):
        return self.node_info.get_pod_node_name(pod_name, namespace)
    
    
    def getPodResourceRequest(self, filename):
        return self.podResourceYAMLManager.get(filename)


    def extractUniqueNamespacesFromPods(self, pod_requests):
        return list({pod_info['namespace'] for pod_info in pod_requests.values()})


    def findNodesByNamespaces(self, node_metrics, namespaces):
        return {
            namespace: [
                node_name for node_name, node_data in node_metrics.items()
                if namespace in node_data['namespaces_on_node']
            ]
            for namespace in namespaces
        }


    def normalize_available_resources_node(self, node_metrics):
        #노드 가용 자원
        normalized_cpu = node_metrics['allocatable_resources']['allocatable_cpu'] / self.node_info.max_cpu_cores
        normalized_memory = node_metrics['allocatable_resources']['allocatable_memory'] / self.node_info.max_memory_mb
        return round(min(normalized_cpu, normalized_memory), 2)


    def normalize_resources_pod(self, cpu, memory):
        normalized_cpu = cpu / self.node_info.max_cpu_cores
        normalized_memory = memory / self.node_info.max_memory_mb
        return round((normalized_cpu + normalized_memory) / 2, 1)


    def findMaxResourceUsageByOtherNamespaces(self, node_name, current_namespace):
        # 현재 네임스페이스를 제외한 모든 네임스페이스에 대해 자원 사용량 확인
        node_metric = self.get_node_metric[node_name]
        max_usage = 0
        
        for namespace, usage in node_metric['namespace_resources'].items():
            if namespace != current_namespace:
                normalize_resources = self.normalize_resources_pod(usage['cpu'], usage['memory'])
                max_usage = max(max_usage, normalize_resources)
        return max_usage
    
 

    def update_node_resources(self, node_name, pod_cpu_request, pod_memory_request):
        """
        선택된 노드에서 요청된 파드의 자원 만큼 빼서 업데이트
        """
        self.get_node_metric[node_name]['allocatable_resources']['allocatable_cpu'] -= pod_cpu_request
        self.get_node_metric[node_name]['allocatable_resources']['allocatable_memory'] -= pod_memory_request
        return self.get_node_metric
        


    def checkNodeResourceAvailabilityForPod(self, node_metrics, pod):
        # 노드에서 할당 가능한 CPU와 메모리 얻기
        allocatable_cpu = node_metrics['allocatable_resources']['allocatable_cpu']
        allocatable_memory = node_metrics['allocatable_resources']['allocatable_memory']
        
        # 파드에서 요청하는 CPU와 메모리 얻기
        requested_cpu = pod['requests']['cpu']
        requested_memory = pod['requests']['memory']
        
        # 노드에 충분한 자원이 있는지 확인
        if requested_cpu <= allocatable_cpu and requested_memory <= allocatable_memory:
            return True  # 충분한 자원이 있음
        else:
            return False  # 자원 부족
    

    def get_replacementpod(self, namespace, traffic_map, base_node):
        replacementpod_different_node = {}
        
        for source_pod in traffic_map:
            for target_pod in traffic_map[source_pod]:
                latency = 0.001
                source_pod_node = self.getNodeName(source_pod, namespace)
                target_pod_node = self.getNodeName(target_pod, namespace)
                
                if source_pod_node != base_node or target_pod_node != base_node:                  
                    #temp[source_pod][target_pod]: [전송 횟수. 전송량]
                    taffic_5m = round(traffic_map[source_pod][target_pod][1], 2) #MB로
                    data_size = round(traffic_map[source_pod][target_pod][1] / traffic_map[source_pod][target_pod][0] / 1024 * 1024, 1) #MB로s
                    
                    if taffic_5m > self.threshold:
                        replacementpod_different_node[f'{source_pod}/{target_pod}'] = taffic_5m 
                    
        replacementpod_different_node = sorted(replacementpod_different_node.items(), key=lambda item: item[1], reverse=True)
        replacementpod_different_node = dict(replacementpod_different_node)
        
        return replacementpod_different_node
                

    def making_group(self):    

        replacement_pods = self.select_replacement_pod()
        temp_groups = {}

        for key in replacement_pods.keys():
            client, server = key.split('/')

            if server not in temp_groups:
                temp_groups[server] = set()
            temp_groups[server].add(client)

        # 각 그룹을 튜플로 결합
        groups = set()
        for server, clients in temp_groups.items():
            group = tuple(sorted(clients)) + (server,)
            groups.add(group)

        return groups
    
    
    def find_nodes_by_latency(self, base_node):
        latency_list = []
        seen_nodes = set()

        for nodes, latency in self.istio_info.latency_dict.items():
            if base_node in nodes:
                node1, node2 = nodes.split('-')
                other_node = node1 if base_node != node1 else node2

                if other_node not in seen_nodes:
                    latency_list.append((other_node, latency))
                    seen_nodes.add(other_node)

        sorted_latency_list = sorted(latency_list, key=lambda x: x[1])

        return [node for node, _ in sorted_latency_list]

    
    def in_node_resource(self, node, pod_requests):
        self.allocatable_resources[node]['allocatable_cpu'] = self.allocatable_resources[node]['allocatable_cpu'] - pod_requests['cpu'] 
        self.allocatable_resources[node]['allocatable_memory'] = self.allocatable_resources[node]['allocatable_memory'] - pod_requests['memory']
    
    def out_node_resource(self, node, pod_requests):
        self.allocatable_resources[node]['allocatable_cpu'] = self.allocatable_resources[node]['allocatable_cpu'] + pod_requests['cpu'] 
        self.allocatable_resources[node]['allocatable_memory'] = self.allocatable_resources[node]['allocatable_memory'] + pod_requests['memory']
    
    
    def check_pod_out(self, base_node, temp_exchange_pod, namespace): # 안에 있던 거 넣는거
        latencies_to_base = {node: latency for node, latency in self.istio_info.latency_dict.items() if base_node in node}
        sorted_latencies = sorted(latencies_to_base.items(), key=lambda x: x[1])

        for node_pair, latency in sorted_latencies:

            target_node = node_pair.replace(base_node, '').replace('-', '')

            if target_node == base_node:  
                continue

            enough_resources = self.check_resources_for_pod(target_node, temp_exchange_pod, namespace)
            
            if enough_resources:
                print(f"Moving {temp_exchange_pod} from {base_node} to {target_node}")
                return 1  
        else:
            print("No suitable node found to move the pod")
            return 0


    def check_resources_for_pod(self, node, pod_name, namespace):
        pod_requests = self.node_info.get_pod_requests(pod_name, namespace)
        need_cpu = self.allocatable_resources[node]['allocatable_cpu'] - pod_requests['cpu']
        need_memory = self.allocatable_resources[node]['allocatable_memory'] - pod_requests['memory']
        if need_cpu >= 0 and need_memory >= 0:
            return 1
        else:
            return 0

    def find_node_to_move_base_node_pod(self, pod_name, base_node, namespace):
        candidate_nodes = self.find_nodes_by_latency(base_node)
        pod_requests = self.node_info.get_pod_requests(pod_name, namespace) # 파드의 자원 가져오기
        select_node = 'none'
        
        for candidate_node in candidate_nodes:
            if candidate_node == 'master': continue
            need_cpu = self.allocatable_resources[candidate_node]['allocatable_cpu'] - pod_requests['cpu']
            need_memory = self.allocatable_resources[candidate_node]['allocatable_memory'] - pod_requests['memory']   
            if need_cpu >= 0 and need_memory >= 0: # 파드 안 빼도 자원이 있는 경우
                self.in_node_resource(base_node, pod_requests)
                select_node = candidate_node
                break
        return select_node


    def run_kubectl_command(self, command, file):
        try:
            result = subprocess.run(["kubectl", command, "-f", file], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e.stderr}")

    
    def move_pod(self, node_name, pod_name, namespace): #파드 옮길 시
        yaml_path = f'/home/dnclab/hokun/kube/code/scheduler/pods_yaml/{namespace}/{pod_name}.yaml'
        self.run_kubectl_command("delete", yaml_path)
        self.podResourceYAMLManager.add_node_selector(yaml_path, node_name)
        self.run_kubectl_command("create", yaml_path)
        print(f'{pod_name} move to {node_name}')
        #kubectl create -f yaml

        
    def find_base_node_with_namespace(self, namespace):  
        with open(self.base_node_json, 'r') as json_file:
            data = json.load(json_file)
            
        for key, value in data.items():
            if namespace in value:
                return key
            
        return None

    def read_json_as_dict(self):
        with open(self.base_node_json, 'r') as file:
            return json.load(file)


            
        
    def replacement(self):
        
        self.allocatable_resources = self.node_info.get_actual_allocatable_resources()
        namespaces_sort = self.node_info.get_pod_counts_per_namespace(self.namespaces) # 파드를 많이 소유하고 있는 namespace부터 우선 고려
        # 네임스페이스
        
        for namespace in namespaces_sort:   
            print('===========================================') 
            base_node = self.find_base_node_with_namespace(namespace)  
            traffic_map = self.istio_info_dict.get(namespace) # 네임스페이스 내 파드 간 통신 map
            candidate_pods = self.istio_info_dict.calculate_node_traffic(base_node, traffic_map, namespace)  # 베이스 노드의 파드 찾기
            replacementpods_different_node = self.get_replacementpod(namespace, traffic_map, base_node)  ### 베이스 노드 밖에서 통신을 자주 하고 있는 파드   
            
            print('namespace, basenode:', namespace, base_node)
            print('namespace_base_node:', base_node)
            print('candidate_pods:', candidate_pods)
            print('replacementpods_different_node:', replacementpods_different_node)
            
            # 베이스 노드 밖에서 다른 파드와 통신하는 애들 중 임계값 넘는 애들 베이스로 불러오는 부분
            for replacementpod_different_node in replacementpods_different_node: # 가장 베이스 노드 밖에서 통신을 자주 하고 있는 파드 순으로
                pod_names = replacementpod_different_node.split('/') # 파드 쌍 출력
            
                for pod_name in pod_names:
                    current_pod_node = self.node_info.get_pod_node_name(pod_name, namespace) # 현재 해당 파드의 위치
                    
                    if current_pod_node != base_node:
                        pod_requests = self.node_info.get_pod_requests(pod_name, namespace) # 파드의 자원 가져오기
                        need_cpu = self.allocatable_resources[base_node]['allocatable_cpu'] - pod_requests['cpu']
                        need_memory = self.allocatable_resources[base_node]['allocatable_memory'] - pod_requests['memory']
                                 
                        if need_cpu >= 0 and need_memory >= 0: # 파드 안 빼도 자원이 있는 경우
                            self.in_node_resource(base_node, pod_requests)
                            self.move_pod(base_node, pod_name, namespace)
                            
                        else: # 베이스 노드 안에 있는 애들 중 통신 별로 안 하는 애들 밖으로 빼는 부분
                            exchange_pods = []
                            add_cpu = 0
                            add_memory = 0
                            check = 0
                            
                            for candidate_pod, score in candidate_pods.items():
                                if score > self.threshold: 
                                    break

                                candidate_pod_resource = self.node_info.get_pod_requests(candidate_pod, namespace)
                                add_cpu = add_cpu + candidate_pod_resource['cpu']
                                add_memory = add_memory + candidate_pod_resource['memory']
                                exchange_pods.append(candidate_pod)
                                
                                if need_cpu + add_cpu >= 0 and need_memory + add_memory >= 0: # 파드 빼면 자원이 생긴다면
                                    for exchange_pod in exchange_pods:
                                        exchange_pod_requests = self.node_info.get_pod_requests(exchange_pod, namespace)
                                        self.out_node_resource(base_node, exchange_pod_requests)  
                                    self.in_node_resource(base_node, pod_requests)  
                                    check = 1
                                    break
    
                            if check == 1: # 밖에 있던 파드를 안에 넣고 안에 있던 파드를 밖으로 뺌
                                for exchange_pod in exchange_pods:
                                    candidate_pods.pop(exchange_pod, None) 
                                    target_node = self.find_node_to_move_base_node_pod(exchange_pod, base_node, namespace)
                                    print('target_node', target_node)
                                    self.move_pod(target_node, exchange_pod, namespace) # 있던 파드 뺌
                                self.move_pod(base_node, pod_name, namespace) #밖에 있던 파드 안에 넣음
                                    
                                    
                            else: # 밖에 있던 파드를 안에 넣을 자리가 없어, 베이스 노드와 가장 지연시간이 짧은 노드 찾음
                                target_node = self.find_node_to_move_base_node_pod(candidate_pod, base_node, namespace)
                                self.move_pod(target_node, candidate_pod, namespace)
            
            print('===========================================') 
                                
                                


start_time = time.time()
sc = Replacement()
sc.replacement()
end_time = time.time()
print(f"Time taken: {round(end_time - start_time, 2)} seconds")
