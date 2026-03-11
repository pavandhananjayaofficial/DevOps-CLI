# DevAI Layer-Wise Architecture

This document breaks down the DevAI system into fundamental layers to establish a scalable, secure, and deterministic architecture.

## 1. Interface Layer
- **Purpose:** Provide the primary interaction points for users to communicate their deployment and infrastructure management intents.
- **Responsibilities:**
  - Accept natural language input or structured commands.
  - Present multi-turn conversation UI or CLI dialogs.
  - Render deployment plans, status updates, and execution streamed output.
- **Modules:**
  - [cli](file:///f:/github/DevOps-CLI/devai/interfaces/cli.py#13-17): Terminal-based interface (Click/Rich).
  - `web_api`: REST/GraphQL (FastAPI) serving the web frontend.
  - `chat_ui`: Web frontend (e.g., React/Next.js).
- **Technologies:** Click, Rich, FastAPI, React.
- **Interfaces with:** `Memory Layer` (to load conversation context), `Planning Layer` (to send intents), `Execution Layer` (to subscribe to real-time status).
- **Development Complexity:** Low (CLI) to Medium (Web API & UI).

## 2. Intent & Memory Layer (AI Agent Layer)
- **Purpose:** Understand what the user wants, maintain context across multi-turn sessions, and categorize intent.
- **Responsibilities:**
  - Parse raw text into structured [Intent](file:///f:/github/DevOps-CLI/devai/intent/parser.py#3-26) objects (Deploy, Destroy, Status, Drift Check).
  - Retrieve and update conversational history.
  - Load previous state or infrastructure footprints to provide context to the Planner.
- **Modules:**
  - `parser`: NLP or LLM-based categorization of the text.
  - `memory`: Database connection managing sessions and states.
- **Technologies:** Pydantic (data structures), SQLite/PostgreSQL, small local NLP models (e.g., spacy) or LLM fast-calls.
- **Interfaces with:** `Interface Layer` (receives text), `Planning Layer` (passes enriched intent).
- **Development Complexity:** Medium.

## 3. Planning Layer (AI & Validation)
- **Purpose:** The core brain that translates user intent and memory context into a strictly structured deployment plan.
- **Responsibilities:**
  - Construct prompts for the underlying LLMs (Local, OpenAI, Anthropic).
  - Generate declarative JSON/YAML infrastructure plans.
  - **Crucial:** Validate the generated plan against deterministic schemas and security policies. If the AI hallucinates bad infrastructure, it is caught here.
- **Modules:**
  - `planner`: The LLM orchestration engine.
  - `models`: The Pydantic definitions defining valid infrastructure.
  - `validator`: The deterministic rule engine enforcing schemas and policies.
- **Technologies:** `openai`, `anthropic`, `llama.cpp`, Pydantic, JSON Schema.
- **Interfaces with:** `Intent Layer` (takes input), `Execution Layer` (passes fully validated plans).
- **Development Complexity:** High (Handling LLM hallucinations and designing comprehensive validation schemas).

## 4. Execution Layer
- **Purpose:** The deterministic engine that takes a locked, validated plan and makes the exact state changes required.
- **Responsibilities:**
  - Parse the [DeploymentPlan](file:///f:/github/DevOps-CLI/devai/core/models.py#21-29).
  - Resolve dependencies (e.g., create Network before VM).
  - Dispatch required actions to the appropriate Infrastructure Connectors.
  - Stream logs back up to the Interface.
- **Modules:**
  - `engine`: Orchestrator and DAG (Directed Acyclic Graph) resolver.
  - `state_manager`: Records the actual applied state back to the Memory layer.
- **Technologies:** Python `asyncio` (for parallel deployment), NetworkX (for dependency graphs).
- **Interfaces with:** `Planning Layer` (receives valid plan), `Infrastructure Connectors` (executes commands).
- **Development Complexity:** High (Handling state, retries, rollbacks, and parallel execution).

## 5. Infrastructure Connectors Layer
- **Purpose:** Adapters that perform the actual mutation of cloud resources or local infrastructure.
- **Responsibilities:**
  - Translate the generic [ResourceDefinition](file:///f:/github/DevOps-CLI/devai/core/models.py#11-20) properties into tool-specific API calls or CLI executions (e.g., translating a generic `container` definition into `docker run...`).
  - Capture concrete resource IDs or ARNs post-creation.
- **Modules:**
  - `connectors`: Individual implementations (e.g., DockerConnector, AWSConnector, TerraformConnector).
- **Technologies:** `boto3` (AWS), `docker-py` (Docker), `kubernetes-client` (K8s).
- **Interfaces with:** `Execution Layer` (receives exact commands).
- **Development Complexity:** Medium (per connector, but high total surface area).

## 6. Plugin Layer
- **Purpose:** Provide an extensible architecture for the community to add new providers or validation rules without modifying the core.
- **Responsibilities:**
  - Dynamically load Python modules or external binaries.
  - Register new Connectors, AI Models, or Validation Policies.
- **Modules:**
  - `registry`: System to register and discover plugins.
- **Technologies:** Python `importlib`, entry points (`pluggy`).
- **Interfaces with:** `Planning Layer` (custom AI), `Validation Layer` (custom rules), `Infrastructure Connectors` (custom clouds).
- **Development Complexity:** Medium.

---

## Recommended Implementation Order

To build a scalable and testable system, I recommend the following build order (iterative expansion):

1. **Step 1: The Core Data Pipeline (Done)**
   - Define the [DeploymentPlan](file:///f:/github/DevOps-CLI/devai/core/models.py#21-29) schemas (Pydantic).
   - *Why: Everything in the system revolves around this deterministic data model.*

2. **Step 2: Planning Layer (AI + Validation)**
   - Build the connections to OpenAI/Anthropic/Local.
   - Build the robust Validation Engine.
   - *Why: The system's value is in translating text to valid plans. Without a strict validation layer, the AI cannot be trusted.*

3. **Step 3: Execution Layer + Minimal Connectors**
   - Build the Execution DAG and a simple connector (e.g., local Docker).
   - *Why: Allows for immediate end-to-end testing of the AI's output executing safely on a local machine.*

4. **Step 4: Interface & Memory Layer**
   - Solidify the CLI, add SQLite memory tracking.
   - *Why: Enables multi-turn conversations and state tracking out of memory.*

5. **Step 5: Cloud Connectors & Web API**
   - Expand connectors to AWS/K8s. Build the FastAPI layer.
   - *Why: Graduates the tool from a local toy to a production Cloud tool.*

6. **Step 6: Plugin Layer**
   - Formalize the plugin interfaces so developers can contribute.
   - *Why: Needed for long-term open-source scaling.*
