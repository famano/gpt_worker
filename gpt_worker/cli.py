"""
GPT Worker Command Line Interface
"""
import os
import sys
import json
import click
from typing import Optional

from gpt_worker.constants import DEFAULT_MODEL, DEFAULT_WORKSPACE_DIR, GPT_WORKER_DIR, PLAN_FILE, STATE_SUMMARY_FILE
from gpt_worker.agents import DataHolder, Orchestrator

def setup_workspace(directory: str) -> None:
    """Setup and validate workspace directory"""
    if not os.path.exists(directory):
        click.echo(f"Error: Directory '{directory}' does not exist", err=True)
        sys.exit(1)

@click.group()
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """GPT Worker - AI Task Automation Tool"""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

@cli.command()
@click.argument('order', required=False)
@click.option('--model', '-m', default=DEFAULT_MODEL, help='LLM model to use')
@click.option('--directory', '-d', default=DEFAULT_WORKSPACE_DIR, help='Working directory')
@click.pass_context
def run(ctx, order: Optional[str], model: str, directory: str):
    """Execute tasks"""
    try:
        setup_workspace(directory)
        
        # Load task list and state summary
        tasklist = []
        state_summary = ""

        # Load task list
        plan_dir = os.path.join(directory, PLAN_FILE)
        if os.path.exists(plan_dir):
            with open(plan_dir, encoding="utf-8") as f:
                tasklist = json.loads(f.read())
            if ctx.obj["verbose"]:
                click.echo(f"Loaded task list: {plan_dir}")

        # Load state summary
        summary_dir = os.path.join(directory, STATE_SUMMARY_FILE)
        if os.path.exists(summary_dir):
            with open(summary_dir, encoding="utf-8") as f:
                state_summary = f.read()
            if ctx.obj["verbose"]:
                click.echo(f"Loaded state summary: {summary_dir}")

        dataholder = DataHolder(
            tasklist=tasklist,
            state_summary=state_summary,
            workspace_dir=directory
        )
        orchestrator = Orchestrator(dataholder=dataholder)
        
        if ctx.obj["verbose"]:
            click.echo(f"Model: {model}")
            click.echo(f"Directory: {directory}")
        
        for message in orchestrator.run(order=order if order else "", model=model):
            click.echo("------")
            if ctx.obj["verbose"]:
                click.echo(f"role: {message['role']}")
            
            if message["role"] == "tool":
                content = json.loads(message["content"])
                success = content.get("success", False)
                click.echo(f"Tool execution: {'success' if success else 'failure'}")
                if not success and ctx.obj["verbose"]:
                    click.echo(f"Error: {content.get('content', 'Unknown error')}")
            else:
                if "content" in message:
                    click.echo("Agent:")
                    click.echo(message["content"])
                
                if "tool_calls" in message:
                    click.echo("tool_calls:")
                    click.echo(message["tool_calls"]["function"])
                
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('directory', required=False, default=DEFAULT_WORKSPACE_DIR)
@click.pass_context
def init(ctx, directory: str):
    """Initialize a new workspace"""
    try:
        # Create base directory
        if not os.path.exists(directory):
            os.makedirs(directory)
            if ctx.obj["verbose"]:
                click.echo(f"Created directory: {directory}")
        
        # Create .gpt_worker directory
        gpt_worker_dir = os.path.join(directory, GPT_WORKER_DIR)
        if not os.path.exists(gpt_worker_dir):
            os.makedirs(gpt_worker_dir)
            if ctx.obj["verbose"]:
                click.echo(f"Created GPT Worker directory: {gpt_worker_dir}")
        
        # Create initial files
        plan_path = os.path.join(directory, PLAN_FILE)
        if not os.path.exists(plan_path):
            with open(plan_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            if ctx.obj["verbose"]:
                click.echo(f"Created task list file: {plan_path}")
        
        summary_path = os.path.join(directory, STATE_SUMMARY_FILE)
        if not os.path.exists(summary_path):
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("")
            if ctx.obj["verbose"]:
                click.echo(f"Created state summary file: {summary_path}")
        
        click.echo(f"Initialized workspace '{directory}'")
        
    except Exception as e:
        click.echo(f"Error: Failed to initialize workspace: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--directory', '-d', default=DEFAULT_WORKSPACE_DIR, help='Working directory')
def list(directory: str):
    """Display current task list"""
    try:
        setup_workspace(directory)
        
        plan_path = os.path.join(directory, PLAN_FILE)
        if not os.path.exists(plan_path):
            click.echo("Task list does not exist")
            return

        with open(plan_path, encoding="utf-8") as f:
            tasks = json.loads(f.read())
            
        if not tasks:
            click.echo("Task list is empty")
            return
            
        for i, task in enumerate(tasks, 1):
            click.echo(f"\nTask {i}:")
            click.echo(json.dumps(task, ensure_ascii=False, indent=2))
        
    except Exception as e:
        click.echo(f"Error: Failed to display task list: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--directory', '-d', default=DEFAULT_WORKSPACE_DIR, help='Working directory')
def status(directory: str):
    """Display current state summary"""
    try:
        setup_workspace(directory)
        
        summary_path = os.path.join(directory, STATE_SUMMARY_FILE)
        if not os.path.exists(summary_path):
            click.echo("State summary does not exist")
            return

        with open(summary_path, encoding="utf-8") as f:
            summary = f.read()
            
        if not summary:
            click.echo("State summary is empty")
            return
            
        click.echo("\n=== State Summary ===\n")
        click.echo(summary)
        
    except Exception as e:
        click.echo(f"Error: Failed to display state summary: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli(obj={})
