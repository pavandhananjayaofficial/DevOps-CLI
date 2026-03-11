# DevAI Phase 5: AI Infrastructure Platform

Phase 5 transforms DevAI into a **full AI-powered infrastructure platform** for teams, managing environments, access control, and policies.

## 1. Architecture Design

We move from "Single User / Single Project" to a **Multi-Tenant / Multi-Environment** model.

```
Request → Auth/Policy Check → Project/Env Resolver → Engine → Infrastructure
```

---

## 2. New Modules & Responsibilities

| Module | Location | Responsibility |
|--------|----------|----------------|
| `AuthManager` | `auth/auth_manager.py` | Role-Based Access Control (RBAC) |
| `ProjectManager` | `projects/project_manager.py` | Logical grouping of services/resources |
| `EnvManager` | `environment/env_manager.py` | dev/staging/prod isolation and config sync |
| `PolicyEngine` | `policy/policy_engine.py` | Enforces resource limits and security rules |
| `TemplateRegistry` | `templates/template_registry.py` | Catalog of reusable infra/app blueprints |
| `PluginManager` | `plugins/plugin_manager.py` | Handles dynamic loading of external extensions |

---

## 3. Platform Workflow

1.  **Auth**: User login and role verification.
2.  **Environment Selection**: Target `staging` or `production`.
3.  **Policy Validation**: Ensure the request doesn't exceed quota or violate security.
4.  **Template Application**: Load standard architecture from the marketplace.
5.  **Execution**: Apply changes across the selected environment.

---

## Proposed Changes

### Auth & Permissions
#### [NEW] [auth_manager.py](file:///f:/github/DevOps-CLI/devai/auth/auth_manager.py)
Logic for roles (Admin, Developer, Viewer) and session management.

### Hierarchy (Projects & Environments)
#### [NEW] [project_manager.py](file:///f:/github/DevOps-CLI/devai/projects/project_manager.py)
Stores project metadata and links resources.

#### [NEW] [env_manager.py](file:///f:/github/DevOps-CLI/devai/environment/env_manager.py)
Management of environment variables and infrastructure isolation.

### Governance
#### [NEW] [policy_engine.py](file:///f:/github/DevOps-CLI/devai/policy/policy_engine.py)
Pre-execution hook to validate plans against organizational constraints.

### Reusability
#### [NEW] [template_registry.py](file:///f:/github/DevOps-CLI/devai/templates/template_registry.py)
JSON/YAML based templates for common stacks (FastAPI+Postgres, etc).

---

## 4. CLI Extensions
- `devai project create <name>`
- `devai env switch <target>`
- `devai template list`
- `devai template use <name>`
- `devai auth login`

---

## Verification Plan

### Automated Tests
- Test policy rejection (e.g., trying to deploy 100 replicas in a dev env).
- Test role-based access (Viewer trying to [destroy](file:///f:/github/DevOps-CLI/devai/connectors/base.py#14-17) a cluster).
- Synchronize configurations between staging and production.

### Manual Verification
- Review RBAC mappings in the SQLite DB.
- Deploy a project using a template.
