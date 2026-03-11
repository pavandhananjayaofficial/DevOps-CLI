# DevAI 🚀

DevAI is an open-source AI-native DevOps system that allows you to deploy infrastructure and applications using natural language.

## 🌟 Key Features
- **Natural Language Deployment:** "deploy a redis container" or "scale the web server to 3 replicas".
- **Deterministic Action:** AI generates plans, but native Python code executes them safely.
- **DAG Orchestration:** Intelligently resolves resource dependencies before execution.
- **Plugin System:** Easily add new AI providers or cloud connectors.
- **Memory System:** Context-aware AI that remembers your previous deployments.

## 🛠️ Installation

1. **Clone the repo:**
   ```bash
   git clone https://github.com/pavandhananjayaofficial/DevOps-CLI.git
   cd DevOps-CLI
   ```

2. **Setup Environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   pip install -e .
   ```

3. **Configure API Keys:**
   ```bash
   set OPENAI_API_KEY=sk-...
   # OR
   set ANTHROPIC_API_KEY=...
   ```

## 🚀 Usage

### CLI Mode
```bash
devai deploy "deploy a nginx server with docker"
```

### Web UI Mode
```bash
python -m devai.interfaces.web
# Open http://localhost:8000
```

## 📖 Documentation
- [Architecture](ARCHITECTURE.md)
- [Roadmap](ROADMAP.md)
- [AI Context](ai_context.md)
- [Contributing](CONTRIBUTING.md)
