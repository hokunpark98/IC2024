import yaml
import os

class PodResourceYAMLManager:
    def __init__(self):
        self.base_output_directory = '/home/dnclab/hokun/kube/code/scheduler/pods_yaml/'

    def memoryStringToMegabytes(self, mem_string):
        if "Ki" in mem_string:
            return int(mem_string.strip("Ki")) / 1024
        elif "Mi" in mem_string:
            return int(mem_string.strip("Mi"))
        elif "Gi" in mem_string:
            return int(mem_string.strip("Gi")) * 1024


    def extractPodResourcesAndCreateYaml(self):
        with open(self.input_filename, 'r') as file:
            docs = list(yaml.safe_load_all(file))

        pod_resources = {}

        for doc in docs:
            if doc and doc['kind'] == 'Pod':
                pod_name = doc['metadata']['name']
                namespace = doc['metadata']['namespace']
                containers = doc['spec']['containers']

                namespace_directory = os.path.join(self.base_output_directory, namespace)
                if not os.path.exists(namespace_directory):
                    os.makedirs(namespace_directory)

                pod_yaml_filename = f"{namespace_directory}/{pod_name}.yaml"
                with open(pod_yaml_filename, 'w') as pod_file:
                    yaml.dump(doc, pod_file)

                for container in containers:
                    resource_requests = container['resources']['requests']

                    # Convert memory string to megabytes
                    if 'memory' in resource_requests:
                        memory_in_mb = self.memoryStringToMegabytes(resource_requests['memory'])
                        resource_requests['memory'] = memory_in_mb

                    pod_resources[pod_name] = {
                        'namespace': namespace,
                        'requests': resource_requests,
                        'yaml_file': pod_yaml_filename
                    }

        return pod_resources


    def add_node_selector_to_pods_in_yaml(self, file_name, pod_to_node_map):
        # Load the YAML file
        with open(file_name, 'r') as file:
            documents = list(yaml.safe_load_all(file))
            updated_docs = []

            # Iterate over the documents and add the node selector to the specified pods
            for doc in documents:
                if doc is not None and doc['kind'] == 'Pod':
                    pod_name = doc['metadata']['name']
                    if pod_name in pod_to_node_map:
                        node_name = pod_to_node_map[pod_name]
                        if 'spec' not in doc:
                            doc['spec'] = {}
                        doc['spec']['nodeSelector'] = {'key': node_name}
                updated_docs.append(doc)

        # Write the updated YAML back to the file
        with open(file_name, 'w') as file:
            yaml.safe_dump_all(updated_docs, file)
            
            
    def add_node_selector(self, yaml_path, node_name):
        try:
            # Load the YAML file
            with open(yaml_path, 'r') as file:
                docs = list(yaml.safe_load_all(file))

            updated_docs = []

            # Iterate over the documents and add the node selector to the Pod
            for doc in docs:
                if doc is not None and doc.get('kind', '') == 'Pod':
                    if 'spec' not in doc:
                        doc['spec'] = {}
                    doc['spec']['nodeSelector'] = {'key': node_name}

                updated_docs.append(doc)

            # Write the updated YAML back to the file
            with open(yaml_path, 'w') as file:
                yaml.safe_dump_all(updated_docs, file)

            print(f"Updated nodeSelector for {yaml_path} to {node_name}")

        except Exception as e:
            print(f"Error updating {yaml_path}: {e}")


            
    def get(self, input_filename):
        self.input_filename = input_filename
        pod_resources = self.extractPodResourcesAndCreateYaml()
        return pod_resources


if __name__ == "__main__":
    root_directory = "/home/dnclab/hokun/kube/code/scheduler/bench"

    pod_resource_extractor = PodResourceYAMLManager()

    # Recursively traverse the directory and its subdirectories
    for root, _, files in os.walk(root_directory):
        for filename in files:
            # Check if the file has a ".yaml" extension
            if filename.endswith(".yaml"):
                # Construct the full path to the YAML file
                full_path = os.path.join(root, filename)
                
                # Process the YAML file and get pod resources
                result = pod_resource_extractor.get(full_path)
                print(f"Processed: {full_path}")
                print(result)