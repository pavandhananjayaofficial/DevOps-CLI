# DevAI Full Architecture Blueprint & Roadmap (v2)

Based on the new requirements, DevAI will be expanded from a simple MVP to a fully featured AI DevOps platform.

## 1. System Analysis & Gaps
The existing prototype provides the foundation for Layers 1-7. However, to meet the full vision, we need to implement:
- **Comprehensive Configuration:** `~/.devai/config.yaml` to manage providers and active models.
- **Enhanced CLI:** Support for `start`, `logs`, `status`, `doctor`, and interactive `/model` commands.
- **Local LLM Layer:** Integration with `llama.cpp` for privacy-first operations.
- **DevOps Phase Expansion:** Moving from mock Docker to real SSH/VPS and project detection.

## 2. Updated Layer Architecture
### Layer 1: Interface (CLI + Web UI)
- **CLI:** Interactive loop (REPL) using `prompt_toolkit`.
- **Web UI:** React-based dashboard served via `devai start`.

### Layer 2: Intent & Model Manager [EXPANDED]
- Responsible for parsing both natural language and slash commands (e.g., `/model use`).

### Layer 3: AI Planning (Multi-Provider)
- Abstracted `BaseAIProvider` with implementations for:
  - `OpenAIProvider`
  - `AnthropicProvider`
  - `LlamaCppProvider` (Local)

### Layer 4-8: (Validation, Execution, Connectors, Memory, Plugins)
- Continue following the existing "AI-Plans | Code-Executes" principle.

## 3. Proposed Development Phases

### Phase 1: Foundation & Model Management (Current Focus)
- [ ] Implement `ConfigManager` to handle `~/.devai/config.yaml`.
- [ ] Implement Model Switching logic and `/model` CLI commands.
- [ ] Add `LlamaCppProvider` placeholder for Local LLM.

### Phase 2: Enhanced Orchestration & VPS
- [ ] Implement `SSHConnector` for VPS deployments.
- [ ] Add FastAPI project detection (Phase 1 task in brief).
- [ ] Implement `devai status` and `devai logs`.

### Phase 3: Cloud & Monitoring
- [ ] AWS/Kubernetes Connectors.
- [ ] Basic infrastructure monitoring.

## 4. MVP Recommendation
The first priority for the new MVP is **Model Management**. The user must be able to configure their provider (Local vs Cloud) immediately upon installation.

### Implementation Step 1:
Create the `devai/core/config.py` manager and update the [AIPlanner](file:///f:/github/DevOps-CLI/devai/ai/planner.py#11-151) to be model-agnostic based on the config.
