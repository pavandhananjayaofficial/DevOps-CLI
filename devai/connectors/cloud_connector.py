from typing import Dict, Any, List, Optional
from devai.utils.core.exceptions import DevAIException

class CloudConnector:
    """
    Abstract cloud provider connector.
    Handles server creation, destruction, and listing across providers.
    Concrete implementations: AWSConnector, DigitalOceanConnector.
    """

    SUPPORTED_PROVIDERS = ["aws", "digitalocean", "mock"]

    def __init__(self, provider: str = "mock", credentials: Optional[Dict[str, str]] = None):
        self.provider = provider
        self.credentials = credentials or {}

    def create_server(self, name: str, region: str = "us-east-1", size: str = "s-1vcpu-1gb") -> Dict[str, Any]:
        """Provisions a new cloud server. Returns connection info."""
        print(f"[Cloud/{self.provider.upper()}] 🌐 Provisioning server '{name}' in {region}...")
        if self.provider == "mock":
            import time, random
            time.sleep(0.5)  # simulate API call
            ip = f"10.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,100)}"
            return {"name": name, "ip": ip, "status": "active", "provider": self.provider, "region": region}
        elif self.provider == "digitalocean":
            return self._do_create_server(name, region, size)
        elif self.provider == "aws":
            return self._aws_create_server(name, region, size)
        else:
            raise DevAIException(f"Unsupported provider: {self.provider}")

    def destroy_server(self, server_id: str) -> bool:
        """Destroys a cloud server by ID."""
        print(f"[Cloud/{self.provider.upper()}] 🗑️  Destroying server {server_id}...")
        # Mock: always succeeds
        return True

    def list_servers(self) -> List[Dict[str, Any]]:
        """Lists all servers in this provider account."""
        print(f"[Cloud/{self.provider.upper()}] 📋 Listing servers...")
        # Mock response
        return []

    def apply(self, name: str, properties: Dict[str, Any]) -> None:
        """ExecutionEngine connector interface - creates a server."""
        region = properties.get("region", "us-east-1")
        size = properties.get("size", "s-1vcpu-1gb")
        info = self.create_server(name, region, size)
        print(f"[Cloud] ✅ Server ready: {info['ip']}")

    def destroy(self, name: str, properties: Dict[str, Any]) -> None:
        """ExecutionEngine connector interface - destroys a server."""
        server_id = properties.get("server_id", name)
        self.destroy_server(server_id)

    def _do_create_server(self, name: str, region: str, size: str) -> Dict[str, Any]:
        """DigitalOcean Droplet creation via API."""
        try:
            import requests
            token = self.credentials.get("do_token", "")
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            payload = {"name": name, "region": region, "size": size, "image": "ubuntu-22-04-x64"}
            resp = requests.post("https://api.digitalocean.com/v2/droplets", json=payload, headers=headers)
            resp.raise_for_status()
            droplet = resp.json()["droplet"]
            return {"name": name, "ip": "pending", "id": droplet["id"], "status": droplet["status"]}
        except Exception as e:
            raise DevAIException(f"DigitalOcean API error: {e}")

    def _aws_create_server(self, name: str, region: str, size: str) -> Dict[str, Any]:
        """AWS EC2 instance creation via boto3."""
        try:
            import boto3
            ec2 = boto3.resource("ec2", region_name=region,
                                  aws_access_key_id=self.credentials.get("aws_access_key"),
                                  aws_secret_access_key=self.credentials.get("aws_secret_key"))
            instances = ec2.create_instances(
                ImageId="ami-0c02fb55956c7d316",  # Amazon Linux 2 us-east-1
                MinCount=1, MaxCount=1,
                InstanceType=size,
                TagSpecifications=[{"ResourceType": "instance", "Tags": [{"Key": "Name", "Value": name}]}]
            )
            inst = instances[0]
            inst.wait_until_running()
            inst.reload()
            return {"name": name, "ip": inst.public_ip_address, "id": inst.id, "status": "running"}
        except Exception as e:
            raise DevAIException(f"AWS API error: {e}")
