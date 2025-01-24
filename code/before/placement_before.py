import time
from podResourceYAMLManager import PodResourceYAMLManager
from monitor.nodeMetrics import KubernetesInfo
from monitor.istioMetrics import IstioMetrics
from monitor.pingServer import RTTCollector
import requests


class Scheduler:
    def __init__(self):
        self.node_info = KubernetesInfo()
        self.istio_info = IstioMetrics()
        self.podResourceYAMLManager = PodResourceYAMLManager()
        self.rtt_collector = RTTCollector()
        self.max_cpu_cores = 20
        self.max_memory_mb = 31980
        self.A = 0.5
        self.B = 2
        self.C = 1
    
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


    def getRTTNode(self):
        response = requests.get("http://192.168.0.3:5000/get_rtt")
        return response.json()
    

    def getServiceRequest(self, pod_requets):
        service_request_cpu = 0
        service_request_memory = 0
        
        for pod_name in pod_requets:
            service_request_cpu = service_request_cpu + pod_requets[pod_name]['requests']['cpu']
            service_request_memory = service_request_memory + pod_requets[pod_name]['requests']['memory']
        return service_request_cpu, service_request_memory


    def normalize_available_resources_node(self, node_metrics):
        #노드 가용 자원
        normalized_cpu = node_metrics['allocatable_resources']['allocatable_cpu'] / self.max_cpu_cores
        normalized_memory = node_metrics['allocatable_resources']['allocatable_memory'] / self.max_memory_mb
        return round(min(normalized_cpu, normalized_memory), 2)


    def request_and_available_resources_node(self, node_metrics, service_request_cpu, service_request_memory):
        #노드 가용 자원 대비 요청량
        request_and_available_cpu = service_request_cpu / node_metrics['allocatable_resources']['allocatable_cpu'] 
        request_and_available_memory = service_request_memory / node_metrics['allocatable_resources']['allocatable_memory'] 
        return round(min(request_and_available_cpu, request_and_available_memory), 2)


    def normalize_resources_pod(self, cpu, memory):
        normalized_cpu = cpu / self.max_cpu_cores
        normalized_memory = memory / self.max_memory_mb
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
    
 
    def calNamespaceUsage(self, node_metric, namespace):
        '''
        해당 네임스페이스가 특정 노드에서 사용 중인 자원량 비율 계산 
        ((네임스페이스 CPU 사용량 / 총 CPU 자원)  + (네임스페이스 Memory 사용량 / 총 Memory 자원)) / 2
        '''
        cpu_usage = node_metric['namespace_resources'][namespace]['cpu'] / \
                    node_metric['allocatable_resources']['total_cpu']
        memory_usage = node_metric['namespace_resources'][namespace]['memory'] / \
                             node_metric['allocatable_resources']['total_memory']
        return round((cpu_usage + memory_usage) / 2 , 2)



    def update_node_resources(self, node_name, pod_cpu_request, pod_memory_request):
        """
        선택된 노드에서 요청된 파드의 자원 만큼 빼서 업데이트
        """
        self.get_node_metric[node_name]['allocatable_resources']['allocatable_cpu'] -= pod_cpu_request
        self.get_node_metric[node_name]['allocatable_resources']['allocatable_memory'] -= pod_memory_request
        return self.get_node_metric
        
        
    
    def calTotalResourceUsageByNodeAndNamespace(self, node_name, namespace):
        '''
        특정 노드에 특정 네임스페이스를 가진 파드의 총 자원 사용량
        '''
        # 특정 노드의 메트릭 가져오기
        node_metric = self.get_node_metric[node_name]
        
        # 해당 네임스페이스가 해당 노드에서 사용 중인 자원량 
        cpu_usage = node_metric['namespace_resources'][namespace]['cpu']
        memory_usage = node_metric['namespace_resources'][namespace]['memory']
        normalize_resources = self.normalize_resources_pod(cpu_usage, memory_usage)
       
        # 총 자원 사용량 반환
        return normalize_resources


    def calResourceUsageByNodeAndNamespace(self, get_pod_resource_request):
        '''
        네임스페이스 별 워커 노드에서 사용 중인 자원량
        '''
        extract_unique_namespaces_from_pods = self.extractUniqueNamespacesFromPods(get_pod_resource_request)
        find_nodes_by_namespaces = self.findNodesByNamespaces(self.get_node_metric, extract_unique_namespaces_from_pods)
        node_to_namespace_usage = {}

        for namespace, nodes in find_nodes_by_namespaces.items():
            for node in nodes:
                if node not in node_to_namespace_usage:
                    node_to_namespace_usage[node] = {}
                node_to_namespace_usage[node][namespace] = self.calNamespaceUsage(self.get_node_metric[node], namespace)
        
        return node_to_namespace_usage


    def calResourceUtilizationDifference(self, node_metrics):
        '''
        노드의 CPU와 Memory 자원 사용율 차이 계산
        로드 벨런싱 목적
        '''     
        # 노드의 요청된 CPU와 메모리 자원 얻기
        cpu_usage = node_metrics['allocatable_resources']['requested_cpu_percentage']
        memory_usage = node_metrics['allocatable_resources']['requested_memory_percentage']
        
        # 사용률 차이 계산
        difference = abs(cpu_usage - memory_usage)
        
        # 최소 사용률을 찾아서 차이를 정규화
        min_usage = min(cpu_usage, memory_usage)
        if min_usage == 0:
            return difference  # 0으로 나누기 방지
        return round(difference / min_usage, 2)


    def isNamespaceInCluster(self, namespace):
        for node_metrics in self.get_node_metric.values():
            if namespace in node_metrics['namespaces_on_node']:
                return True
        return False


    def isNamespaceOnNode(self, node_name, namespace):
        node_metrics = self.get_node_metric[node_name]
        
        # 노드 메트릭 정보가 존재하고, 네임스페이스가 해당 노드에 존재하는지 확인
        if node_metrics and namespace in node_metrics['namespaces_on_node']:
            return True  
        return False 



    def sortPodsByResourceRequests(self, pod_requests):
        '''
        서비스에서 요청한 파드를 자원 요청량 순으로 정렬
        min(cpu 요구량 / cpu 요구량 중 가장 큰 것, Memory 요구량 / Memory 요구량 중 가장 큰 것) 이 가장 큰 것
        요구 자원량이 동일하다면 get_pod_resource_request() 순서와 동일하게
        '''
        # 가장 큰 CPU 요구량과 메모리 요구량 찾기
        max_cpu_request = max(pod_info['requests']['cpu'] for pod_info in pod_requests.values())
        max_memory_request = max(pod_info['requests']['memory'] for pod_info in pod_requests.values())
        
        # 정렬 기준 생성: CPU와 메모리 요구량의 정규화된 최솟값
        sorted_pods = sorted(pod_requests.items(), key=lambda item: min(item[1]['requests']['cpu'] / max_cpu_request, item[1]['requests']['memory'] / max_memory_request), reverse=True)
        
        # 정렬된 파드 목록 반환 (파드 이름과 요청 자원량)
        return sorted_pods






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


    def makeBaseNode(self, get_pod_resource_request):
        minScore = 10000
        baseNode = ''
        service_request_cpu, service_request_memory = self.getServiceRequest(get_pod_resource_request)
        
        for node_name, node_metrics in self.get_node_metric.items(): 
            score = self.request_and_available_resources_node(node_metrics, service_request_cpu, service_request_memory)
       
            if score < minScore:
                minScore = score
                baseNode = node_name
                
        return baseNode

    '''
    base노드 선정:
    - 노드의 가용자원 - 0.5 * 노드에 있는 네임스페이스E(노드에 있는 네임스페이스의 다른 노드에 있는 자원의 합)
    
    노드의 가용자원 점수:
    - Min((서비스 요구 CPU / 노드의 가용 CPU), (서비스 요구 메모리 / 노드의 가용 메모리))
    
    base노드에 자리가 없을 시:
    - base노드와 통신 latency가 가장 작은 노드에 배치
    '''
    
    def placement(self, file_name): 
        result = {}
        get_pod_resource_request = self.getPodResourceRequest(file_name)
        sort_pods_by_resource_requests = self.sortPodsByResourceRequests(get_pod_resource_request)  
        self.get_node_metric = self.node_info.get_node_resources_info()
        
        
        '''
        파일 읽어와서 해당 네임스페이스의 베이스노드 유무를 확인 추가하기
        '''
        baseNode = self.makeBaseNode(get_pod_resource_request)
  
        
        # 해당 서비스의 요청된 파드 중 가장 많은 자원을 요구하는 파드부터 배치
        for pod_name, pod_data in sort_pods_by_resource_requests:
            print('-----------------------')
            
            
            
            
            for node_name, node_metrics in self.get_node_metric.items():   
                print('-----------------------')

                # 해당 노드에 파드를 배치할 수 있는지 확인
                availability = self.checkNodeResourceAvailabilityForPod(node_metrics, pod_data)
                #if not availability:
                #    continue 
                
                # 노드의 가용자원 점수

                continue

                   
                #노드별 배치된 같은 namespace인 파드의 총 자원량                  
                cal_resource_usage_by_node_and_namespace = 0
                if self.isNamespaceOnNode(node_name, pod_data['namespace']):
                    cal_resource_usage_by_node_and_namespace = self.calTotalResourceUsageByNodeAndNamespace(node_name, pod_data['namespace'])
                    #print(f'노드명: {node_name}, {pod_data["namespace"]}: {cal_resource_usage_by_node_and_namespace}')
                
                max_usage_by_other_namespaces = self.findMaxResourceUsageByOtherNamespaces(node_name, pod_data['namespace'])
                
                print('nodename', node_name)
                print('pod_name', pod_data['namespace'])

                
            
            print('**********************************')      
   
        self.podResourceYAMLManager.add_node_selector_to_pods_in_yaml(file_name, result)


sc = Scheduler()

file_name = "/home/dnclab/hokun/modified_service1.yaml"
start_time = time.time()
sc.placement(file_name)
end_time = time.time()
print(f"Time taken: {round(end_time - start_time, 2)} seconds")
