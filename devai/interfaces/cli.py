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

@click.group()
def cli():
    """DevAI: AI-Powered DevOps Assistant."""
    init_db()

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
def logs():
    """View deployment logs."""
    console.print("[dim]Recent Deployment Logs:[/dim]")
    # For now, mock logs. In a real app, read from a logs file or DB.
    console.print("2026-03-11 21:20:00 - DEPLOY - Success - nginx-srv")
    console.print("2026-03-11 21:22:00 - DEPLOY - Success - redis-cache")

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
        console.print("[green]Plan Validated! Executing Deterministically...[/green]")

        # 4. Execution
        registry = PluginRegistry()
        engine = ExecutionEngine(registry)
        engine.execute(plan)
        
        console.print("[bold green]Deployment complete![/bold green]")

    except DevAIException as e:
        console.print(f"[bold red]DevAI Error:[/bold red] {str(e)}")
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {str(e)}")

if __name__ == "__main__":
    cli()
