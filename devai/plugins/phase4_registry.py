from devai.plugins.registry import PluginRegistry
from devai.orchestration.kubernetes_manager import KubernetesManager
from devai.cluster.cluster_manager import ClusterManager

def register_phase4_connectors(registry: PluginRegistry):
    """
    Registers Kubernetes and Cluster management connectors.
    """
    # K8s components
    registry.connectors["k8s_deployment"] = KubernetesManager()
    registry.connectors["k8s_cluster"] = ClusterManager("mock")
    print("[Registry] ✅ Registered Phase 4 (K8s) connectors.")
