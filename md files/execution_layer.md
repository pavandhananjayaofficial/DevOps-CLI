# DevAI Execution Layer

Since the exact layer name was left as `[Layer name]`, I am proceeding with the next logical component in our architecture: the **Execution Layer & Infrastructure Connectors**.

## 1. Purpose of this Layer
The Execution Layer is the deterministic "brawn" of DevAI. While the AI Planner dreams up the infrastructure and the Validation Layer ensures it is safe and structurally sound, the Execution Layer actually mutates state. Its purpose is to take a strictly validated [DeploymentPlan](file:///f:/github/DevOps-CLI/devai/core/models.py#21-29), resolve the execution order based on dependencies, and dispatch exact commands to the relevant Infrastructure Connectors (adapters for Docker, AWS, etc.).

## 2. Module Structure
The layer is decoupled from the AI and Interfaces, remaining strictly focused on state application.
```text
devai/
├── execution/
│   ├── __init__.py
│   ├── engine.py       # The DAG resolver and execution orchestrator
│   └── state.py        # (Future) Manages the delta between current and desired state
└── connectors/
    ├── __init__.py
    ├── base.py         # Abstract base class for all connectors
    └── docker.py       # Minimal viable docker implementation
```

## 3. APIs Used By This Layer
- **Input:** [DeploymentPlan](file:///f:/github/DevOps-CLI/devai/core/models.py#21-29) (Pydantic object) passed down from the [SchemaValidator](file:///f:/github/DevOps-CLI/devai/validation/validator.py#5-47).
- **Output:** Execution status, streamed directly to `Console` (CLI) or returned as status objects to the Web UI via generators.
- **External Dependencies:** `docker` SDK (for the [DockerConnector](file:///f:/github/DevOps-CLI/devai/execution/engine.py#9-12)), Cloud SDKs (`boto3`, etc.).

## 4. Design Data Flow
1. **Input:** `engine.execute(validated_plan)` is called.
2. **Dependency Resolution:** The [ExecutionEngine](file:///f:/github/DevOps-CLI/devai/execution/engine.py#13-36) reads all `resources` and their `depends_on` lists to build a standard Directed Acyclic Graph (DAG).
3. **Topological Sort:** The graph is sorted to determine the exact order of execution (e.g., Network must be created before the Server).
4. **Dispatch:** The engine iterates through the sorted order, looking up the appropriate [ConnectorBase](file:///f:/github/DevOps-CLI/devai/execution/engine.py#4-8) implementation in its registry.
5. **Execution:** It calls `connector.apply(resource)` for each infrastructure component.
6. **State Hook:** Returns success/failure metrics back to the caller.

## 5. Minimal Working Implementation
*See the implemented Python files in [devai/execution/engine.py](file:///f:/github/DevOps-CLI/devai/execution/engine.py) and `devai/connectors/base.py`.* The implementation contains a topological sort to handle `depends_on` attributes deterministically.

## 6. Example Usage
```python
from devai.core.models import DeploymentPlan
from devai.execution.engine import ExecutionEngine
from devai.connectors.docker import DockerConnector

# 1. Provide validated plan
plan = DeploymentPlan(
    version="1.0",
    description="Deploying Web App",
    resources=[...]
)

# 2. Initialize Engine & Register Plugins
engine = ExecutionEngine()
engine.register_connector("docker_container", DockerConnector())

# 3. Execute Deterministically
engine.execute(plan)
```
