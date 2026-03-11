# DevAI Phase 2 Design: Enhanced Orchestration & VPS

Phase 2 transforms DevAI from a simple deployment automation tool into a full-fledged VPS orchestration system using Docker as the primary runtime.

## 1. Module Responsibilities

### [NEW] Infrastructure Management
- **`devai.core.server_manager.ServerManager`**: Manages the persistence of VPS server metadata (IP, username, health status) in the Secure Vault/Database.
- **`devai.connectors.vps_connector.VPSConnector`**: (Refining [SSHConnector](file:///f:/github/DevOps-CLI/devai/connectors/ssh.py#5-75)) High-level wrapper for SSH operations including file transfers and command batching.

### [NEW] Execution & Orchestration
- **`devai.execution.ssh_executor.SSHExecutor`**: specialized component for running remote commands with logging and error capture.
- **`devai.execution.docker_manager.DockerManager`**: Generates and manages `docker-compose.yml` files and container lifecycles on the remote VPS.
- **`devai.server.deployment_manager.DeploymentManager`**: Orchestrates the remote filesystem structure (`/opt/devai/apps/{project}`) and environment variables.

## 2. Deployment Workflow

1. **Detection**: [ProjectDetector](file:///f:/github/DevOps-CLI/devai/core/detector.py#4-48) identifies project type and dependencies.
2. **Planning**: AI Planner generates a multi-service JSON plan (e.g., API + Redis).
3. **Validation**: [SchemaValidator](file:///f:/github/DevOps-CLI/devai/validation/validator.py#5-54) ensures the plan follows Phase 2 resource rules.
4. **Execution**:
   - **Step 4a (Local)**: Generate `docker-compose.yml` and `.env` files.
   - **Step 4b (Remote)**: `VPSConnector` ensures `/opt/devai/apps/{name}` exists.
   - **Step 4c (Remote)**: Transfer files to the VPS.
   - **Step 4d (Remote)**: `DockerManager` runs `docker compose up -d`.
5. **Memory**: [StateManager](file:///f:/github/DevOps-CLI/devai/memory/state_manager.py#7-59) records the success and metadata for `devai status`.

## 3. Command Map

| Command | Category | Responsibility |
|---------|----------|----------------|
| `devai server add` | Server Mgmt | Registers a VPS and runs Auto-Setup. |
| `devai server list`| Server Mgmt | Lists healthy vs offline servers. |
| `devai deploy` | Orchestration | Triggers the full deployment workflow. |
| `devai status` | Monitoring | Shows project health & container status. |
| `devai logs` | Monitoring | Streams remote container logs. |
| `devai restart/stop`| Orchestration | Direct container control via SSH. |

## 4. Remote Structure
```text
/opt/devai/apps/{project_name}/
├── docker-compose.yml
├── .env
├── logs/
└── backups/ (Phase 3)
```
