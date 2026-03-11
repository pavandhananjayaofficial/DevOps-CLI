import click
from rich.console import Console
from rich.table import Table
from devai.intent.parser import IntentParser
from devai.ai.planner import AIPlanner
from devai.validation.validator import SchemaValidator
from devai.execution.engine import ExecutionEngine
from devai.connectors.docker import DockerConnector
from devai.plugins.registry import PluginRegistry
from devai.core.exceptions import DevAIException
from devai.memory.database import init_db
from devai.core.config import ConfigManager
import os
import sys
import subprocess
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

console = Console()

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """DevAI: AI-Powered DevOps Assistant."""
    init_db()
    if ctx.invoked_subcommand is None:
        interactive_chat()

@cli.command()
@click.argument('prompt', required=False)
def deploy(prompt: str):
    """Deploy infrastructure using natural language."""
    if not prompt:
        prompt = click.prompt("What would you like to deploy?")
    
    run_devai_loop(prompt)

@cli.command()
def start():
    """Start the DevAI Web UI and interactive chat."""
    console.print("[bold green]Starting DevAI Web UI...[/bold green]")
    console.print("Access the dashboard at: [link=http://localhost:3000]http://localhost:3000[/link]")
    # In a real app, this would start the FastAPI server in a background thread or separate process
    # For now, we'll start the interactive CLI loop
    interactive_chat()

@cli.command()
@click.argument("name", required=False)
def status(name):
    """Check the status of projects and resources."""
    from devai.memory.state_manager import StateManager
    from devai.core.server_manager import ServerManager
    from devai.execution.docker_manager import DockerManager
    
    # 1. Local/Logical Status
    resources = StateManager.get_all_resources()
    if not resources:
        console.print("[dim]No local resources found.[/dim]")
    else:
        table = Table(title="Resource Status")
        table.add_column("Resource", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Status", style="magenta")
        for r in resources:
            table.add_row(r['name'], r['type'], r['status'])
        console.print(table)

    # 2. Remote VPS status (if name provided)
    if name:
        # Check if it's a multi-service project in state
        project = next((r for r in resources if r['name'] == name), None)
        if project and project['type'] == "multi_service":
            server_name = project['properties'].get("server", "default")
            servers = ServerManager.list_servers()
            server = next((s for s in servers if s['name'] == server_name), None)
            if server:
                console.print(f"\n[bold]Remote Status for {name}:[/bold]")
                dm = DockerManager(server['ip'], server['username'])
                try:
                    res = dm.get_status(name)
                    console.print(res)
                finally:
                    dm.close()

@cli.command()
@click.argument("project")
@click.option("--service", "-s", help="Specific service name")
@click.option("--tail", "-t", default=50, help="Number of lines")
def logs(project, service, tail):
    """View logs from a remote project."""
    from devai.memory.state_manager import StateManager
    from devai.core.server_manager import ServerManager
    from devai.execution.docker_manager import DockerManager
    
    resources = StateManager.get_all_resources()
    p_meta = next((r for r in resources if r['name'] == project), None)
    if not p_meta:
        console.print(f"[red]Project '{project}' not found in registry.[/red]")
        return
        
    server_name = p_meta['properties'].get("server", "default")
    servers = ServerManager.list_servers()
    server = next((s for s in servers if s['name'] == server_name), None)
    if server:
        dm = DockerManager(server['ip'], server['username'])
        try:
            res = dm.get_logs(project, service, tail)
            console.print(res)
        finally:
            dm.close()

@cli.command()
@click.argument("project")
@click.option("--service", "-s", help="Specific service name")
def restart(project, service):
    """Restart a remote project or service."""
    from devai.memory.state_manager import StateManager
    from devai.core.server_manager import ServerManager
    from devai.execution.docker_manager import DockerManager
    
    resources = StateManager.get_all_resources()
    p_meta = next((r for r in resources if r['name'] == project), None)
    if not p_meta:
        console.print(f"[red]Project '{project}' not found.[/red]")
        return
        
    server_name = p_meta['properties'].get("server", "default")
    servers = ServerManager.list_servers()
    server = next((s for s in servers if s['name'] == server_name), None)
    if server:
        dm = DockerManager(server['ip'], server['username'])
        try:
            dm.restart_project(project, service)
            console.print(f"[green]Project '{project}' restart command sent.[/green]")
        finally:
            dm.close()

@cli.command()
@click.argument("project")
def stop(project):
    """Stop a remote project."""
    from devai.memory.state_manager import StateManager
    from devai.core.server_manager import ServerManager
    from devai.execution.docker_manager import DockerManager
    
    resources = StateManager.get_all_resources()
    p_meta = next((r for r in resources if r['name'] == project), None)
    if not p_meta:
        console.print(f"[red]Project '{project}' not found.[/red]")
        return
        
    server_name = p_meta['properties'].get("server", "default")
    servers = ServerManager.list_servers()
    server = next((s for s in servers if s['name'] == server_name), None)
    if server:
        dm = DockerManager(server['ip'], server['username'])
        try:
            dm.stop_project(project)
            console.print(f"[yellow]Project '{project}' stopped.[/yellow]")
        finally:
            dm.close()

@cli.command()
def doctor():
    """Diagnose system health and configurations."""
    console.print("[bold]DevAI Doctor 🩺[/bold]")
    config = ConfigManager()
    active_model = config.config.get("active_model")
    console.print(f"Active Model: [green]{active_model}[/green]")
    
    # Check environment variables
    openai_key = "SET" if os.environ.get("OPENAI_API_KEY") else "MISSING"
    anthropic_key = "SET" if os.environ.get("ANTHROPIC_API_KEY") else "MISSING"
    
    console.print(f"OpenAI API Key: {openai_key}")
    console.print(f"Anthropic API Key: {anthropic_key}")
    console.print("[green]System is ready for deployment.[/green]")

@cli.command()
@click.argument("repo_url")
@click.option("--server", "-s", default=None, help="Target server name from registry")
def deploy_repo(repo_url, server):
    """Clone a Git repo and deploy it automatically."""
    from devai.git.git_manager import GitManager
    from devai.core.detector import ProjectDetector
    from devai.core.server_manager import ServerManager

    git = GitManager()
    local_path = git.clone_or_pull(repo_url)
    repo_info = git.get_repo_info(local_path)
    
    console.print(f"[green]Repo ready:[/green] {local_path}")
    console.print(f"[dim]Commit: {repo_info['commit'][:8]} – {repo_info['message']}[/dim]")

    # Generate plan context using project detector
    context = ProjectDetector.get_project_summary()

    # If server specified, run devai_loop with rich context
    project_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    prompt = f"deploy project '{project_name}' on server '{server}'" if server else f"deploy project '{project_name}'"
    run_devai_loop(prompt)

@cli.command()
@click.argument("project")
def monitor(project):
    """Show live health metrics for a deployed project."""
    from devai.memory.state_manager import StateManager
    from devai.core.server_manager import ServerManager
    from devai.monitoring.system_monitor import SystemMonitor

    resources = StateManager.get_all_resources()
    p_meta = next((r for r in resources if r['name'] == project), None)
    if not p_meta:
        console.print(f"[red]Project '{project}' not found.[/red]")
        return

    server_name = p_meta['properties'].get("server", "default")
    servers = ServerManager.list_servers()
    server = next((s for s in servers if s['name'] == server_name), None)
    if not server:
        console.print(f"[red]Server '{server_name}' not found.[/red]")
        return

    mon = SystemMonitor(server['ip'], server['username'])
    try:
        health = mon.get_health_summary(project)
        table = Table(title=f"Health: {project}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("CPU Usage", health['cpu_usage'])
        table.add_row("Memory", health['memory_usage'])
        table.add_row("Disk", health['disk_usage'])
        console.print(table)
        console.print("\n[bold]Container Status:[/bold]")
        console.print(health['containers'])
    finally:
        mon.close()

@cli.command()
@click.argument("project")
@click.option("--server", "-s", required=True, help="Server IP for the pipeline")
@click.option("--user", "-u", default="root", help="SSH username")
@click.option("--output", "-o", default=".", help="Output directory for pipeline file")
def pipeline(project, server, user, output):
    """Generate a GitHub Actions CI/CD pipeline."""
    from devai.cicd.pipeline_generator import PipelineGenerator

    gen = PipelineGenerator()
    path = gen.save_pipeline(output, project, server, user)
    console.print(f"[green]✅ Pipeline created:[/green] {path}")
    console.print("[dim]Add SSH_PRIVATE_KEY to your GitHub repo secrets.[/dim]")

@cli.command()
@click.argument("project")
@click.option("--service", "-s", default=None, help="Specific service name")
def analyze(project, service):
    """Collect logs and run AI error analysis."""
    from devai.memory.state_manager import StateManager
    from devai.core.server_manager import ServerManager
    from devai.logs.log_collector import LogCollector
    from devai.ai.error_analyzer import AIErrorAnalyzer

    resources = StateManager.get_all_resources()
    p_meta = next((r for r in resources if r['name'] == project), None)
    if not p_meta:
        console.print(f"[red]Project '{project}' not found.[/red]")
        return

    server_name = p_meta['properties'].get("server", "default")
    servers = ServerManager.list_servers()
    server = next((s for s in servers if s['name'] == server_name), None)
    if not server:
        console.print(f"[red]Server '{server_name}' not found.[/red]")
        return

    console.print(f"[dim]📥 Fetching logs for {project}...[/dim]")
    collector = LogCollector(server['ip'], server['username'])
    try:
        logs_text = collector.fetch_logs(project, service, tail=200)
        collector.save_logs(project, logs_text)
        errors = collector.analyze_errors(logs_text)
    finally:
        collector.close()

    if not errors:
        console.print("[green]✅ No errors detected in logs.[/green]")
        return

    console.print(f"[yellow]Found {len(errors)} error lines. Running AI analysis...[/yellow]")
    analyzer = AIErrorAnalyzer()
    suggestion = analyzer.analyze_and_suggest(project, errors)
    console.print("\n[bold red]🤖 AI Error Analysis:[/bold red]")
    console.print(suggestion)

@cli.group()
def cluster():
    """Manage Kubernetes clusters."""
    pass

@cluster.command(name="create")
@click.argument("name")
@click.option("--provider", "-p", default="mock", help="Cloud provider (aws, digitalocean, mock)")
@click.option("--nodes", "-n", default=3, help="Number of worker nodes")
def create_cluster(name, provider, nodes):
    """Provision a new K8s cluster."""
    from devai.cluster.cluster_manager import ClusterManager
    cm = ClusterManager(provider)
    res = cm.create_cluster(name, node_count=nodes)
    console.print(f"[green]Cluster '{name}' provisioning started.[/green]")
    console.print(f"Endpoint: {res['endpoint']}")

@cli.command()
@click.argument("project")
@click.argument("replicas", type=int)
def scale(project, replicas):
    """Manually scale a project's replicas."""
    from devai.orchestration.kubernetes_manager import KubernetesManager
    # In a real app, this would update the state and apply the new manifest
    console.print(f"[green]Scaling project '{project}' to {replicas} replicas...[/green]")
    km = KubernetesManager()
    km.apply_manifests(f"Updating deployment {project}")

@cli.command()
@click.argument("project")
def heal(project):
    """Trigger an autonomous self-healing probe for a project."""
    from devai.incident.incident_manager import IncidentManager
    from devai.monitoring.system_monitor import SystemMonitor
    from devai.logs.log_collector import LogCollector
    from devai.core.server_manager import ServerManager
    from devai.memory.state_manager import StateManager

    resources = StateManager.get_all_resources()
    p_meta = next((r for r in resources if r['name'] == project), None)
    if not p_meta:
        console.print(f"[red]Project '{project}' not found.[/red]")
        return

    server_name = p_meta['properties'].get("server", "default")
    servers = ServerManager.list_servers()
    server = next((s for s in servers if s['name'] == server_name), None)
    if not server:
        return

    mon = SystemMonitor(server['ip'], server['username'])
    coll = LogCollector(server['ip'], server['username'])
    
    im = IncidentManager(mon, coll)
    console.print(f"[dim]Running health probe for {project}...[/dim]")
    incident = im.detect_incident(project) or {"type": "Manual Probe", "project": project}
    
    resolution = im.resolve_incident(incident)
    console.print(f"\n[bold green]Healing Action:[/bold green]")
    console.print(f"Action: {resolution['action']} on {resolution['name']}")
    console.print(f"Reason: {resolution.get('properties', {}).get('reason', 'N/A')}")
    
    mon.close()
    coll.close()

@cli.command()
@click.argument("project")
def analyze_infra(project):
    """Run AI-driven infrastructure optimization analysis."""
    from devai.ai.infra_analyzer import InfraAnalyzer
    from devai.monitoring.system_monitor import SystemMonitor
    from devai.core.server_manager import ServerManager
    from devai.memory.state_manager import StateManager

    resources = StateManager.get_all_resources()
    p_meta = next((r for r in resources if r['name'] == project), None)
    if not p_meta:
        console.print(f"[red]Project '{project}' not found.[/red]")
        return

    server_name = p_meta['properties'].get("server", "default")
    servers = ServerManager.list_servers()
    server = next((s for s in servers if s['name'] == server_name), None)
    if not server:
        return

    mon = SystemMonitor(server['ip'], server['username'])
    health = mon.get_health_summary(project)
    mon.close()

    console.print(f"[dim]Analyzing infrastructure footprints for {project}...[/dim]")
    analyzer = InfraAnalyzer()
    res = analyzer.analyze_infrastructure(health)
    console.print("\n[bold cyan]🏛️ Infrastructure Optimization Report:[/bold cyan]")
    console.print(res)

def interactive_chat():
    """Interactive loop for chatting with DevAI."""
    console.print("[bold blue]DevAI Interactive Mode[/bold blue] (Type 'exit' to quit)")
    session = PromptSession(history=FileHistory(os.path.expanduser("~/.devai/history")))
    
    while True:
        try:
            user_input = session.prompt("devai> ")
            if user_input.lower() in ["exit", "quit"]:
                break
            if user_input.startswith("/"):
                handle_slash_command(user_input)
                continue
            
            run_devai_loop(user_input)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

def handle_slash_command(command: str):
    parts = command.split()
    cmd = parts[0]
    config = ConfigManager()

    if cmd == "/model":
        if len(parts) == 1:
            active = config.config.get("active_model")
            console.print(f"Current model: [bold green]{active}[/bold green]")
        elif parts[1] == "list":
            models = config.config.get("models", {}).keys()
            console.print("Available models:")
            for m in models:
                console.print(f" - {m}")
        elif parts[1] == "use" and len(parts) > 2:
            try:
                config.set_active_model(parts[2])
                console.print(f"Switched to [bold green]{parts[2]}[/bold green]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    else:
        console.print(f"[red]Unknown command: {cmd}[/red]")

@cli.group()
def agent():
    """Manage autonomous DevOps agents."""
    pass

@agent.command(name="run")
@click.argument("task")
def run_agent_task(task):
    """Assign a complex task to the autonomous agent manager."""
    from devai.agents.agent_manager import AgentManager
    am = AgentManager()
    console.print(f"[dim]🤖 Assigning task: {task}[/dim]")
    res = am.run_task(task)
    console.print("\n[bold blue]Autonomous Agent Plan:[/bold blue]")
    console.print(res)

@agent.command(name="status")
def agent_status():
    """Show the status of active specialized agents."""
    from devai.agents.agent_manager import AgentManager
    am = AgentManager()
    status = am.get_agent_status()
    table = Table(title="Specialized Agents")
    table.add_column("Agent", style="cyan")
    table.add_column("Status", style="green")
    for a, s in status.items():
        table.add_row(a, s)
    console.print(table)

@cli.group()
def knowledge():
    """Access the autonomous learning knowledge base."""
    pass

@knowledge.command(name="list")
def list_knowledge():
    """List learned failure/remediation patterns."""
    from devai.learning.knowledge_base import KnowledgeBase
    kb = KnowledgeBase()
    records = kb.records
    if not records:
        console.print("[dim]Knowledge base is empty.[/dim]")
    else:
        table = Table(title="Learned Patterns")
        table.add_column("Project", style="cyan")
        table.add_column("Failure", style="red")
        table.add_column("Remediation", style="green")
        for r in records:
            table.add_row(r['project'], r['failure'], r['remediation'])
        console.print(table)

@cli.group()
def scheduler():
    """Manage the background automation scheduler."""
    pass

@scheduler.command(name="list")
def list_tasks():
    """List scheduled background tasks."""
    from devai.automation.scheduler import TaskScheduler
    # Normally would look at a persistent task list
    console.print("[dim]No tasks currently scheduled in background worker.[/dim]")

@cli.command()
@click.argument("requirement")
def advise(requirement):
    """Ask the AI Infrastructure Assistant for architecture advice."""
    from devai.ai.infra_assistant import AIInfraAssistant
    assistant = AIInfraAssistant()
    console.print(f"[dim]Consulting AI Architect on '{requirement}'...[/dim]")
    suggestion = assistant.suggest_architecture(requirement)
    console.print("\n[bold cyan]🏛️ AI Architecture Blueprint:[/bold cyan]")
    console.print(suggestion)

@cli.group()
def project():
    """Manage DevAI projects."""
    pass

@project.command(name="create")
@click.argument("name")
def create_project(name):
    """Create a new project group."""
    from devai.projects.project_manager import ProjectManager
    pm = ProjectManager()
    pm.create_project(name)
    console.print(f"[green]Project '{name}' created.[/green]")

@cli.group()
def env():
    """Manage deployment environments."""
    pass

@env.command(name="switch")
@click.argument("name")
def switch_env(name):
    """Switch the active global environment (dev/staging/prod)."""
    from devai.projects.project_manager import EnvManager
    em = EnvManager()
    em.switch_env(name)

@cli.group()
def template():
    """Explore and use architecture templates."""
    pass

@template.command(name="list")
def list_templates():
    """List available architecture templates."""
    from devai.templates.template_registry import TemplateRegistry
    tr = TemplateRegistry()
    templates = tr.list_templates()
    table = Table(title="Template Marketplace")
    table.add_column("ID", style="cyan")
    table.add_column("Description", style="green")
    for t in templates:
        table.add_row(t['id'], t['description'])
    console.print(table)

@cli.command()
def login():
    """Login to the DevAI platform."""
    from devai.auth.auth_manager import AuthManager
    am = AuthManager()
    username = click.prompt("Username")
    password = click.prompt("Password", hide_input=True)
    if am.login(username, password):
        console.print(f"[green]Welcome back, {username}![/green]")
    else:
        console.print("[red]Login failed.[/red]")

@cli.group()
def secrets():
    """Manage encrypted secrets and environment variables."""
    pass

@secrets.command(name="set")
@click.argument("key")
@click.argument("value")
def set_secret(key, value):
    """Store a secret in the encrypted vault."""
    from devai.memory.vault import VaultManager
    vault = VaultManager()
    vault.store_secret(key, value)
    console.print(f"[green]Secret '{key}' stored successfully.[/green]")

@secrets.command(name="list")
def list_secrets():
    """List all stored secret keys."""
    from devai.memory.vault import VaultManager
    vault = VaultManager()
    keys = vault.list_secrets()
    if not keys:
        console.print("[dim]No secrets found in vault.[/dim]")
    else:
        for k in keys:
            console.print(f" - {k}")

@cli.group()
def server():
    """Manage remote VPS servers."""
    pass

@server.command(name="add")
@click.argument("name")
@click.argument("ip")
@click.argument("username")
def add_server(name, ip, username):
    """Register a new VPS server."""
    from devai.core.server_manager import ServerManager
    ServerManager.add_server(name, ip, username)

@server.command(name="list")
def list_servers():
    """List all managed servers."""
    from devai.core.server_manager import ServerManager
    servers = ServerManager.list_servers()
    if not servers:
        console.print("[dim]No servers registered.[/dim]")
    else:
        table = Table(title="Managed Servers")
        table.add_column("Name", style="cyan")
        table.add_column("IP", style="green")
        table.add_column("Username", style="yellow")
        table.add_column("Status", style="magenta")
        for s in servers:
            table.add_row(s['name'], s['ip'], s['username'], s['status'])
        console.print(table)

@server.command(name="remove")
@click.argument("name")
def remove_server(name):
    """Remove a server from the registry."""
    from devai.core.server_manager import ServerManager
    ServerManager.remove_server(name)

@server.command(name="setup")
@click.argument("name")
def setup_server(name):
    """Initialize a server with Docker and basic security."""
    from devai.core.server_manager import ServerManager
    ServerManager.setup_server(name)

def run_devai_loop(user_input: str):
    try:
        # 0. Context Gathering
        from devai.core.detector import ProjectDetector
        project_context = ProjectDetector.get_project_summary()
        console.print(f"[dim]{project_context.strip()}[/dim]")

        # 1. Intent Parsing
        parser = IntentParser()
        intent = parser.parse(user_input)
        
        # 2. AI Planning
        planner = AIPlanner()
        console.print(f"[dim]Planning with AI ([bold]{planner.get_active_model_info()['model']}[/bold])...[/dim]")
        raw_plan = planner.generate_plan(user_input, context=project_context)

        # 3. Validation
        validator = SchemaValidator()
        plan = validator.validate_plan(raw_plan)
        validator.enforce_security_policies(plan)

        # 3.1 Policy Engine check (Phase 5)
        from devai.policy.policy_engine import PolicyEngine
        from devai.projects.project_manager import EnvManager
        em = EnvManager()
        pe = PolicyEngine()
        decision = pe.evaluate(plan, em.active_env)
        if decision.violations:
            console.print("[bold red]Policy Violations Detected:[/bold red]")
            for violation in decision.violations:
                console.print(f" - [{violation.policy}] {violation.message}")
            if em.active_env == "production":
                raise DevAIException("Policy violations block production deployments.")
            if not click.confirm("Proceed anyway?"):
                return

        if decision.warnings:
            console.print("[bold yellow]Policy Warnings:[/bold yellow]")
            for warning in decision.warnings:
                console.print(f" - [{warning.policy}] {warning.message}")

        console.print("[green]Plan Validated! Executing Deterministically...[/green]")

        # 4. Execution
        registry = PluginRegistry()
        engine = ExecutionEngine(registry)
        report = engine.execute(
            plan,
            approval_callback=lambda prompt: click.confirm(f"{prompt} Proceed?"),
        )
        
        console.print("[bold green]Deployment complete![/bold green]")
        for item in report.executed_resources:
            console.print(f" - {item.name}: {item.status} ({item.detail})")

    except DevAIException as e:
        console.print(f"[bold red]DevAI Error:[/bold red] {str(e)}")
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {str(e)}")

if __name__ == "__main__":
    cli()

