# DevAI Context for AI Agents

This file provides high-level context for AI Coding Assistants working on DevAI.

## Implementation Rules
1. **No Mixed Logic:** AI must never generate strings intended for `eval()` or `subprocess.run()` directly.
2. **Strict Typing:** All new code must use Python type hints and pass `pyright`.
3. **Layer Integrity:** Interfaces must not talk directly to Connectors. They must go through the Planner and Execution Engine.
4. **Pydantic Models:** Use `devai.core.models` for all cross-layer data exchange.

## Project Structure
- `devai/core`: Shared models and exceptions.
- `devai/ai`: AI provider communication logic.
- `devai/execution`: Graph-based orchestration.
- `devai/memory`: DB models and state managers.
- `devai/plugins`: Registry for dynamic loading.

## Typical Task Workflow
1. Analyze user request in the Interface.
2. Update `AIPlanner` prompts if new JSON schema fields are added.
3. Update `SchemaValidator` to enforce any new safety rules.
4. Implement/Update `Connector` in `devai/connectors`.
5. Register connector in `devai/plugins/registry.py` (or via entry points).
