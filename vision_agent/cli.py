#!/usr/bin/env python3
"""CLI for VisionAgent."""

import os
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def get_agent(**kwargs):
    """Create VisionAgent instance."""
    from .core import VisionAgent
    
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Error: OPENAI_API_KEY environment variable not set[/red]")
        sys.exit(1)
    
    return VisionAgent(**kwargs)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """👁️ VisionAgent - AI that can see and interact with any UI."""
    pass


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
def analyze(image_path):
    """Analyze a screenshot and describe its contents."""
    agent = get_agent()
    result = agent.analyze(image_path)
    
    console.print(Panel.fit(f"[bold blue]📸 Analysis: {image_path}[/bold blue]"))
    console.print(f"\n{result.description}\n")
    
    if result.elements:
        console.print("[bold]Interactive Elements:[/bold]")
        for i, el in enumerate(result.elements[:10], 1):
            console.print(f"  {i}. [{el.element_type}] {el.description} at ({el.x}, {el.y})")


@cli.command()
@click.argument("description")
@click.option("--screenshot", "-s", type=click.Path(exists=True), help="Screenshot to search in")
def find(description, screenshot):
    """Find a specific element on screen."""
    agent = get_agent()
    
    if not screenshot:
        console.print("📸 Taking screenshot...")
        screenshot = agent._take_screenshot()
    
    element = agent.find_element(description, screenshot)
    
    if element:
        console.print(f"[green]✅ Found![/green]")
        console.print(f"   Element: {element.description}")
        console.print(f"   Type: {element.element_type}")
        console.print(f"   Location: ({element.x}, {element.y})")
        console.print(f"   Confidence: {element.confidence*100:.0f}%")
    else:
        console.print(f"[red]❌ Element not found: {description}[/red]")


@cli.command("click")
@click.argument("x", type=int)
@click.argument("y", type=int)
@click.option("--dry-run", is_flag=True, help="Don't actually click")
def click_cmd(x, y, dry_run):
    """Click at coordinates."""
    agent = get_agent(dry_run=dry_run)
    result = agent.click(x, y)
    
    if result.success:
        console.print(f"[green]✅ {result.details}[/green]")
    else:
        console.print(f"[red]❌ {result.details}[/red]")


@cli.command("type")
@click.argument("text")
@click.option("--dry-run", is_flag=True, help="Don't actually type")
def type_cmd(text, dry_run):
    """Type text."""
    agent = get_agent(dry_run=dry_run)
    result = agent.type_text(text)
    
    if result.success:
        console.print(f"[green]✅ {result.details}[/green]")
    else:
        console.print(f"[red]❌ {result.details}[/red]")


@cli.command()
@click.argument("direction", type=click.Choice(["up", "down", "left", "right"]))
@click.option("--amount", "-a", default=3, help="Scroll amount")
@click.option("--dry-run", is_flag=True, help="Don't actually scroll")
def scroll(direction, amount, dry_run):
    """Scroll the screen."""
    agent = get_agent(dry_run=dry_run)
    result = agent.scroll(direction, amount)
    
    if result.success:
        console.print(f"[green]✅ {result.details}[/green]")
    else:
        console.print(f"[red]❌ {result.details}[/red]")


@cli.command()
@click.argument("command")
@click.option("--dry-run", is_flag=True, help="Don't execute actions")
def do(command, dry_run):
    """Execute a natural language command."""
    agent = get_agent(dry_run=dry_run)
    
    console.print(f"🤖 Executing: {command}\n")
    result = agent.do(command)
    
    if result.success:
        console.print(f"[green]✅ {result.details}[/green]")
    else:
        console.print(f"[red]❌ {result.details}[/red]")
        if result.error:
            console.print(f"[dim]Error: {result.error}[/dim]")


@cli.command()
@click.argument("steps")
@click.option("--dry-run", is_flag=True, help="Don't execute actions")
def automate(steps, dry_run):
    """Run multi-step automation.
    
    Steps can be provided as a quoted string with numbered items:
    "1. Click the login button
     2. Type 'username' in the field
     3. Click submit"
    """
    agent = get_agent(dry_run=dry_run)
    
    console.print(Panel.fit("[bold blue]🤖 Starting Automation[/bold blue]"))
    result = agent.automate(steps)
    
    console.print(f"\n[bold]Results:[/bold]")
    console.print(f"  Total steps: {result.total_steps}")
    console.print(f"  Completed: {result.completed_steps}")
    console.print(f"  Duration: {result.duration_seconds:.1f}s")
    
    if result.success:
        console.print(f"\n[green]✅ All steps completed successfully![/green]")
    else:
        console.print(f"\n[yellow]⚠️ Some steps failed[/yellow]")
        for step in result.steps:
            if not step.success:
                console.print(f"  - Step {step.step_number}: {step.error}")


@cli.command()
@click.option("--dry-run", is_flag=True, help="Don't execute actions")
def interactive(dry_run):
    """Start interactive mode."""
    agent = get_agent(dry_run=dry_run)
    
    console.print(Panel.fit(
        "[bold blue]👁️ VisionAgent Interactive Mode[/bold blue]\n"
        "Commands: screenshot, analyze, find, click, type, do, quit",
        border_style="blue"
    ))
    
    agent.interactive()


@cli.command()
def screenshot():
    """Take a screenshot."""
    agent = get_agent()
    path = agent._take_screenshot()
    console.print(f"[green]📸 Screenshot saved: {path}[/green]")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
