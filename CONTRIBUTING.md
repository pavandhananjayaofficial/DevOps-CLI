# Contributing to DevAI

Welcome! We are excited to have you contribute to the future of AI-driven DevOps.

## How to Add a New Connector
DevAI is built to be extensible. To add a new cloud provider (e.g., Azure):

1. **Implement the Base Class:**
   Create a new file in `devai/connectors/azure.py` and inherit from `ConnectorBase`.
   
2. **Implement Required Methods:**
   - `apply(resource_name, properties)`
   - `destroy(resource_name, properties)`
   - `read_state(resource_name)`

3. **Register the Plugin:**
   Add an entry point in `pyproject.toml` or register it manually in `devai/plugins/registry.py`.

## Code Style
- Use strict type hints.
- All core logic should be deterministic.
- AI should only be used in the `devai.ai` layer to generate structural data.

## Testing
Run the CLI in mock mode to verify your connector's logic:
```bash
set DEVAI_DEFAULT_PROVIDER=mock
devai deploy "your test prompt"
```
