from kubernetes import client, config
from collections import defaultdict


class KubernetesInfo:
    def __init__(self):
        config.load_kube_config()
        self.core_api = client.CoreV1Api()
        self.max_cpu_cores = 20
        self.max_memory_mb = 31980
        
        
    def cpu_string_to_core(self, cpu_string):
        if "m" in cpu_string:
            return round(float(cpu_string.strip("m")) / 1000, 1)
        else:
            return round(float(cpu_string), 1)
        
    def memory_string_to_megabytes(self, mem_string):
        if "Ki" in mem_string:
            return int(mem_string.strip("Ki")) / 1024
        elif "Mi" in mem_string:
            return int(mem_string.strip("Mi"))
        elif "Gi" in mem_string:
            return int(mem_string.strip("Gi")) * 1024


    def get_node_available_resources(self, node_name):
        config.load_kube_config()
        v1 = client.CoreV1Api()

        try:
            node = v1.read_node(node_name)
        except client.exceptions.ApiException as e:
            print(f"API Exception: {e}")
            return

        allocatable = node.status.allocatable
        return allocatable


    def get_pod_counts_per_namespace(self, namespaces):
        """
        Counts pods for each namespace and returns a sorted dictionary
        of namespaces and their respective pod counts.
        """
        config.load_kube_config()
        v1 = client.CoreV1Api()

        namespace_pod_counts = defaultdict(int)

        try:
            all_pods = v1.list_pod_for_all_namespaces().items
            for pod in all_pods:
                namespace = pod.metadata.namespace
                if namespace not in namespaces:
                    continue
                namespace_pod_counts[namespace] += 1

            # Sort the dictionary by pod counts in descending order
            sorted_namespace_pod_counts = dict(sorted(namespace_pod_counts.items(), key=lambda item: item[1], reverse=True))
            
            return sorted_namespace_pod_counts

        except client.exceptions.ApiException as e:
            print(f"API Exception: {e}")
            return {}
        

    def get_pod_requests(self, pod_name, namespace):
        config.load_kube_config()
        v1 = client.CoreV1Api()

        try:
            pod = v1.read_namespaced_pod(pod_name, namespace)
        except client.exceptions.ApiException as e:
            print(f"API Exception: {e}")
            return

        requests = {'cpu': 0.0, 'memory': 0.0}
        for container in pod.spec.containers:
            if container.resources.requests:
                requests_cpu =  self.cpu_string_to_core(container.resources.requests.get('cpu', requests['cpu']))
                requests_memory = self.memory_string_to_megabytes(container.resources.requests.get('memory', requests['memory']))
             
                requests['cpu'] =  requests['cpu'] + requests_cpu
                requests['memory'] = requests['memory'] + requests_memory

        return requests


    def get_actual_allocatable_resources(self):
        nodes = self.core_api.list_node().items
        pods = self.core_api.list_pod_for_all_namespaces().items

        result = {}
        for node in nodes:
            node_name = node.metadata.name

            total_memory = self.memory_string_to_megabytes(node.status.capacity["memory"])
            total_cpu = self.cpu_string_to_core(node.status.capacity["cpu"])
           
            requested_memory = 0
            requested_cpu = 0
            
            for pod in [pod for pod in pods if pod.spec.node_name == node_name]:
                for container in pod.spec.containers:
                    if container.resources.requests:
                        if "memory" in container.resources.requests:
                            requested_memory += self.memory_string_to_megabytes(container.resources.requests["memory"])
                        if "cpu" in container.resources.requests:
                            requested_cpu += self.cpu_string_to_core(container.resources.requests["cpu"])
            
            allocatable_memory_Mi = int(total_memory - requested_memory)
            allocatable_cpu = round(total_cpu - requested_cpu, 1)
            result[node_name] = {                
                "allocatable_cpu": allocatable_cpu,
                "allocatable_memory": allocatable_memory_Mi,
                "requested_cpu_percentage": round((requested_cpu / total_cpu) * 100, 1),
                "requested_memory_percentage": round((requested_memory / total_memory) * 100, 1)   
            }

        return result


    def get_pod_count_by_namespace(self, namespace):
        config.load_kube_config()
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace)

        # 클러스터의 모든 노드에 대한 초기 카운트 설정
        node_pod_counts = defaultdict(int)
        nodes = v1.list_node()
        for node in nodes.items:
            # 마스터 노드를 결과에서 제외
            if "master" not in node.metadata.name:
                node_pod_counts[node.metadata.name] = 0

        # 노드별 파드 개수 계산
        for pod in pods.items:
            if pod.spec.node_name in node_pod_counts:
                node_pod_counts[pod.spec.node_name] += 1

        # 가장 파드의 개수가 많은 노드 순으로 정렬
        sorted_nodes = sorted(node_pod_counts, key=lambda node: node_pod_counts[node], reverse=True)

        # 결과 반환
        return sorted_nodes
    

    def get_all_worker_nodes(self):
        """
        Retrieves a list of all worker nodes in the Kubernetes cluster.
        """
        try:
            nodes = self.core_api.list_node().items
            worker_nodes = [node.metadata.name for node in nodes 
                            if 'node-role.kubernetes.io/master' not in node.metadata.labels
                            and node.metadata.name != 'master']
            return worker_nodes
        except client.exceptions.ApiException as e:
            print(f"API Exception: {e}")
            return []
                       

    def get_resources_by_namespace(self):
        v1 = client.CoreV1Api()
        
        nodes = v1.list_node().items
        all_pods = v1.list_pod_for_all_namespaces(watch=False).items
        
        node_to_namespace_resources = {}
        excluded_namespaces = ['istio-system', 'kubeflow', 'gpu-operator', 'auth', 'kube-system', 
                            'knative-eventing', 'local-path-storage', 'knative-serving']

        for node in nodes:
            node_name = node.metadata.name
            node_to_namespace_resources[node_name] = {}

        for pod in all_pods:
            node_name = pod.spec.node_name
            namespace = pod.metadata.namespace

            if namespace in excluded_namespaces or not node_name:
                continue

            if namespace not in node_to_namespace_resources[node_name]:
                node_to_namespace_resources[node_name][namespace] = {"cpu": 0, "memory": 0}

            for container in pod.spec.containers:
                if container.resources.requests:
                    if "memory" in container.resources.requests:
                        node_to_namespace_resources[node_name][namespace]["memory"] += self.memory_string_to_megabytes(container.resources.requests["memory"])
                    if "cpu" in container.resources.requests:
                        node_to_namespace_resources[node_name][namespace]["cpu"] += self.cpu_string_to_core(container.resources.requests["cpu"])
        
        return node_to_namespace_resources

    
    def get_pod_node_name(self, podName, namespace):
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=podName, namespace=namespace)
        node_name = pod.spec.node_name
        return node_name
        
    def get_pods_on_node_in_namespace(self, node_name, namespace):
        """
        Retrieves a list of all pods in the specified namespace that are deployed on the specified node.
        """
        config.load_kube_config()
        v1 = client.CoreV1Api()

        try:
            all_pods = v1.list_namespaced_pod(namespace).items
            pods_on_node = [pod.metadata.name for pod in all_pods if pod.spec.node_name == node_name]
            return pods_on_node
        except client.exceptions.ApiException as e:
            print(f"API Exception: {e}")
            return []


    def get_namespaces_on_node(self, node_name):
        """
        주어진 노드(node_name)에 배치된 모든 네임스페이스의 목록을 중복 없이 반환.
        """
        all_pods = self.core_api.list_pod_for_all_namespaces().items

        namespaces = set()  # 중복을 방지하기 위해 set을 사용

        # 해당 노드에 배치된 파드의 네임스페이스 수집
        for pod in all_pods:
            if pod.spec.node_name == node_name:
                namespaces.add(pod.metadata.namespace)

        return list(namespaces)  # set을 list로 변환하여 반환

        

    def get_namespace_resource_sum_on_node(self, node_name, target_namespace):
        """
        주어진 노드(node_name)에 배치된 특정 네임스페이스(target_namespace)의
        파드들이 요청하는 자원(cpu, memory)의 총합을 계산.
        """
        all_pods = self.core_api.list_pod_for_all_namespaces().items

        resource_sum = {"cpu": 0, "memory": 0}

        # 해당 노드에 배치된 파드의 요청량 계산
        for pod in [pod for pod in all_pods if pod.spec.node_name == node_name and pod.metadata.namespace == target_namespace]:
            for container in pod.spec.containers:
                if container.resources.requests:
                    if "memory" in container.resources.requests:
                        resource_sum["memory"] += self.memory_string_to_megabytes(container.resources.requests["memory"])
                    if "cpu" in container.resources.requests:
                        resource_sum["cpu"] += self.cpu_string_to_core(container.resources.requests["cpu"])

        return resource_sum

    
        
    def get_namespaces_on_all_nodes(self):
        v1 = client.CoreV1Api()
        
        nodes = v1.list_node().items
        all_pods = v1.list_pod_for_all_namespaces(watch=False).items
        
        node_to_namespaces = {}
        excluded_namespaces = ['istio-system', 'kubeflow', 'gpu-operator', 'auth', 'kube-system', 
                               'knative-eventing', 'local-path-storage', 'knative-serving']

        # 각 노드별로 파드의 네임스페이스 정보를 추출
        for node in nodes:
            node_name = node.metadata.name
            node_to_namespaces[node_name] = set()

        for pod in all_pods:
            if pod.spec.node_name in node_to_namespaces and pod.metadata.namespace not in excluded_namespaces:
                node_to_namespaces[pod.spec.node_name].add(pod.metadata.namespace)
        
        # set을 list로 변환
        for node_name, namespaces_set in node_to_namespaces.items():
            node_to_namespaces[node_name] = list(namespaces_set)
        
        return node_to_namespaces


    def get_node_resources_info(self):
        nodes = self.core_api.list_node().items
        pods = self.core_api.list_pod_for_all_namespaces().items

        excluded_namespaces = ['istio-system', 'kubeflow', 'gpu-operator', 'auth', 'kube-system', 
                            'knative-eventing', 'local-path-storage', 'knative-serving']
        node_info = {}
        for node in nodes:
            node_name = node.metadata.name
            # Skip if this is a master node
            if node_name == 'master':
                continue

            total_memory = self.memory_string_to_megabytes(node.status.capacity["memory"])
            total_cpu = self.cpu_string_to_core(node.status.capacity["cpu"])
            requested_memory = 0
            requested_cpu = 0
            namespace_resources = {}
            namespaces_set = set()

            for pod in [pod for pod in pods if pod.spec.node_name == node_name]:
                namespace = pod.metadata.namespace
                if namespace in excluded_namespaces:
                    continue
                
                namespaces_set.add(namespace)
                if namespace not in namespace_resources:
                    namespace_resources[namespace] = {"cpu": 0, "memory": 0}

                for container in pod.spec.containers:
                    if container.resources.requests:
                        if "memory" in container.resources.requests:
                            requested_memory += self.memory_string_to_megabytes(container.resources.requests["memory"])
                            namespace_resources[namespace]["memory"] += self.memory_string_to_megabytes(container.resources.requests["memory"])
                        if "cpu" in container.resources.requests:
                            requested_cpu += self.cpu_string_to_core(container.resources.requests["cpu"])
                            namespace_resources[namespace]["cpu"] += self.cpu_string_to_core(container.resources.requests["cpu"])
            
            allocatable_memory_Mi = int(total_memory - requested_memory)
            allocatable_cpu = round(total_cpu - requested_cpu, 1)
            node_info[node_name] = {
                "allocatable_resources": {
                    "total_cpu": total_cpu,
                    "total_memory": total_memory,
                    "allocatable_cpu": allocatable_cpu,
                    "allocatable_memory": allocatable_memory_Mi,
                    "requested_cpu_percentage": round((requested_cpu / total_cpu), 1),
                    "requested_memory_percentage": round((requested_memory / total_memory), 1)
                },
                "namespace_resources": namespace_resources,
                "namespaces_on_node": list(namespaces_set)
            }

        return node_info
