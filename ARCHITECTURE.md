# DevAI Architecture

DevAI follows a strict **Layered Deterministic AI Pattern**. The AI is responsible for intelligence (planning), while the code is responsible for action (execution).

## Core Principle
**AI → Plans | Code → Executes**

## Layers

### 1. Interface Layer (`devai/interfaces`)
Provides interaction points:
- **CLI:** `click` and `rich` for terminal users.
- **Web UI:** `FastAPI` + Vanilla JS chat interface.

### 2. Intent Parser (`devai/intent`)
Categorizes user input (DEPLOY, DESTROY, STATUS) before AI processing to ensure the model focuses on the correct task.

### 3. AI Planning Layer (`devai/ai`)
Communicates with LLMs (OpenAI, Anthropic) to produce a structural JSON plan. It is strictly prohibited from generating shell commands.

### 4. Validation Layer (`devai/validation`)
Deterministically validates the AI-generated JSON against Pydantic models. Enforces security policies (e.g., no public S3 buckets).

### 5. Execution Engine (`devai/execution`)
Orchestrates resource deployment. It resolves dependencies into a **Directed Acyclic Graph (DAG)** to ensure correct execution order.

### 6. Infrastructure Connectors (`devai/connectors`)
Lightweight wrappers for underlying tools (Docker, AWS SDK, K8s SDK). Connectors provide `apply`, `destroy`, and `read_state` methods.

### 7. Memory System (`devai/memory`)
SQLite persistence tracking:
- **Conversation History:** Context for AI iterations.
- **Resource State:** Record of managed infrastructure.

### 8. Plugin System (`devai/plugins`)
Dynamic loading of new connectors and AI providers via Python entry points.

## Data Flow
User → Intent Parser → AI Planner → **VALIDATOR** → Execution Engine → Connector
