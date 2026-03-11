# DevAI Roadmap

## Phase 1: MVP (Completed)
- [x] CLI interface & layered architecture
- [x] AI Planner (multi-provider: OpenAI, Anthropic, Llama, Mock)
- [x] Docker deployment (local)
- [x] Model management with `/model` commands
- [x] Web UI chat interface
- [x] Memory system (SQLite persistence)

## Phase 2: Enhanced Orchestration & VPS (Completed)
- [x] VPS Server Registry (`devai server` add/list/remove)
- [x] Automatic Server Setup (Docker/Firewall via SSH)
- [x] Multi-Service Orchestration (Docker Compose generation)
- [x] Remote Management (`status`, `logs`, `restart`, `stop`)
- [x] Encrypted Secret Vault
- [x] Multi-Service AI Planning (upgraded JSON schema)

## Phase 3: Cloud Infrastructure & DevOps Automation (In Progress)
- [x] Cloud Provider Support (`CloudConnector` – Mock/DO/AWS)
- [x] Git Integration (`devai deploy-repo <github_url>`)
- [x] CI/CD Pipeline Generation (`devai pipeline` → GitHub Actions YAML)
- [x] Monitoring System (`devai monitor` → CPU/Memory/Containers)
- [x] Logging System (`devai logs`, `devai analyze`)
- [x] AI Error Analysis (logs → errors → AI-suggested fix)
- [ ] Real AWS/DigitalOcean credential integration (Phase 3.1)
- [ ] Live log streaming (`--live` flag with SSH tail -f)

## Phase 4: Kubernetes & Self-Healing
- [ ] Kubernetes manifest generation
- [ ] Helm chart support
- [ ] Auto-scaling policies
- [ ] Self-healing infrastructure (auto-restarts)
- [ ] Multi-cloud cost estimation
- [ ] Advanced security auditing
