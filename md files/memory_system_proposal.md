# Feature Proposal: Layer 7 - Memory & State System

## Analysis of Current State
DevAI currently has a functional pipeline from **Intent** -> **AI Plan** -> **Validation** -> **Execution**. However, it is **stateless**. It does not remember past deployments or previous conversation context. This prevents:
1. **Idempotency:** Re-running a command creates duplicate resources instead of updating.
2. **Stateful Deletes:** Knowing what to delete when a user says "destroy the web server".
3. **Context-Aware AI:** AI doesn't know what it deployed in the previous turn.

## Proposed Feature: The Memory System
The Memory System will provide a persistent core using **SQLite** (for a local CLI experience) to track both conversation threads and infrastructure state.

### 1. Feature Description
A centralized persistence layer that stores:
- **Conversation Logs:** To provide context to the [AIPlanner](file:///f:/github/DevOps-CLI/devai/ai/planner.py#10-140).
- **Infrastructure State:** A record of all resources successfully managed by the [ExecutionEngine](file:///f:/github/DevOps-CLI/devai/execution/engine.py#8-80).

### 2. Affected Layers
- **Layer 7: Memory System** [NEW]
- **Layer 5: Execution Engine** [Update to save/load state]
- **Layer 3: AI Planner** [Update to inject history into prompts]

### 3. Implementation Plan
#### [Component] Memory Layer
##### [NEW] `devai/memory/database.py` (file:///f:/github/DevOps-CLI/devai/memory/database.py)
A lightweight SQLite/SQLAlchemy wrapper for storage.
##### [NEW] `devai/memory/state_manager.py` (file:///f:/github/DevOps-CLI/devai/memory/state_manager.py)
Logic to sync the [ExecutionEngine](file:///f:/github/DevOps-CLI/devai/execution/engine.py#8-80) results with the database.
##### [NEW] `devai/memory/history.py` (file:///f:/github/DevOps-CLI/devai/memory/history.py)
Logic to retrieve recent messages for AI tokens.

#### [Component] Execution & Planning Integration
- **ExecutionEngine:** Call `StateManager.update()` after successful apply/destroy.
- **AIPlanner:** Accept `history` parameter and append to system/user prompts.

### 4. Estimated Complexity
- **Complexity:** 6/10 (Requires careful handling of state transitions and schema versioning).
- **Time Estimate:** ~12 tool calls for a robust initial version.

## User Review Required
> [!IMPORTANT]
> This will introduce a local database file (`.devai.db`) in the user's project directory or home folder. 
> Should we allow users to configure an external database (Postgres) for the Web UI mode?
