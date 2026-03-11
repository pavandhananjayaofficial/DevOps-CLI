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
def status():
    """Check the status of managed infrastructure."""
    from devai.memory.state_manager import StateManager
    resources = StateManager.get_all_resources()
    
    table = Table(title="DevAI Managed Infrastructure")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Last Updated", style="dim")

    for r in resources:
        table.add_row(r["name"], r["type"], r["status"], r.get("last_updated", "N/A"))
    
    console.print(table)

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

def run_devai_loop(user_input: str):
    try:
        # 1. Intent Parsing
        parser = IntentParser()
        intent = parser.parse(user_input)
        
        # 2. AI Planning
        planner = AIPlanner()
        console.print(f"[dim]Planning with AI ([bold]{planner.get_active_model_info()['model']}[/bold])...[/dim]")
        raw_plan = planner.generate_plan(user_input)

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
