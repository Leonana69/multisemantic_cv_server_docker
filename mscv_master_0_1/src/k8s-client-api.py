from kubernetes import client, config

# Load the kubeconfig file
config.load_incluster_config()

# Create a Kubernetes API client
api = client.CoreV1Api()
# List all pods in the current namespace
pods = api.list_namespaced_pod(namespace="default")
for pod in pods.items:
    print(f"Name: {pod.metadata.name}, Status: {pod.status.phase}")