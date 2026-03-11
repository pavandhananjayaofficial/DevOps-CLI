import os
import time
from typing import Dict, Any, List
from devai.core.exceptions import DevAIException

class CloudProvisioner:
    """
    Abstractions for cloud provider APIs to create and manage VPS instances.
    Currently supports mock implementations for AWS and DigitalOcean.
    """
    
    def __init__(self, provider: str = "digitalocean"):
        self.provider = provider

    def provision_vps(self, name: str, region: str = "nyc3", size: str = "s-1vcpu-1gb") -> Dict[str, Any]:
        """
        Simulates provisioning of a new VPS.
        In a real scenario, this would use the DO API or boto3.
        """
        print(f"[{self.provider.upper()}] 🏗️ Provisioning VPS '{name}' in {region} ({size})...")
        time.sleep(2) # Simulate API call
        
        # Mocking a successful provisioning
        ip_address = f"134.209.{os.getpid() % 255}.{int(time.time()) % 255}"
        print(f"[{self.provider.upper()}] ✅ VPS Online! IP: {ip_address}")
        
        return {
            "name": name,
            "ip": ip_address,
            "status": "active",
            "provider": self.provider
        }

    def bootstrap_server(self, ip: str, username: str = "root"):
        """
        Standard bootstrap commands for a fresh VPS.
        """
        bootstrap_commands = [
            "apt-get update",
            "apt-get install -y docker.io",
            "systemctl enable --now docker",
            "ufw allow 22/tcp",
            "ufw allow 80/tcp",
            "ufw allow 443/tcp",
            "ufw --force enable"
        ]
        
        # In a real app, this would return a list of commands for the SSHConnector to run
        return bootstrap_commands
