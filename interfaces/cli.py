"""
Command Line Interface for CyberSage

This module provides a command-line interface to interact with CyberSage's
security tools and agents.
"""

import asyncio
import typer
import rich
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from typing import Optional, List
import yaml
import os
from pathlib import Path

from core.agent_manager import AgentManager
from services.openai_service import OpenAIService
from services.memory_service import MemoryService
from tools.nmap_tool import NmapTool
from tools.whois_tool import WhoisTool
from tools.shodan_tool import ShodanTool

app = typer.Typer(help="CyberSage CLI - AI-powered cybersecurity assistant")
console = Console()

# Load configuration
with open("configs/settings.yaml") as f:
    config = yaml.safe_load(f)

# Initialize services
openai_service = OpenAIService(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=config["services"]["openai"]["model"]
)
memory_service = MemoryService(
    redis_url=config["services"]["redis"]["url"]
)
agent_manager = AgentManager(openai_service, memory_service)


@app.command()
def scan(
    target: str = typer.Argument(..., help="Target to scan"),
    scan_type: str = typer.Option("basic", help="Type of scan to perform"),
    agent_id: str = typer.Option("scanner_agent", help="Agent ID to use")
):
    """Perform a security scan on a target."""
    async def _scan():
        try:
            with Progress() as progress:
                task = progress.add_task("[cyan]Scanning...", total=100)
                
                # Create tools
                nmap_tool = NmapTool()
                
                # Create or get agent
                agent = await agent_manager.get_agent(agent_id)
                if not agent:
                    agent = await agent_manager.create_agent(
                        agent_id=agent_id,
                        agent_type="scanner",
                        tools=[nmap_tool]
                    )
                
                progress.update(task, advance=50)
                
                # Execute scan
                result = await agent.execute_task(
                    f"Perform a {scan_type} scan on {target}"
                )
                
                progress.update(task, advance=50)
                
                # Display results
                console.print("[green]Scan Complete![/green]")
                console.print(result)
                
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
    
    asyncio.run(_scan())


@app.command()
def investigate(
    query: str = typer.Argument(..., help="Investigation query"),
    tools: List[str] = typer.Option(["whois", "shodan"], help="Tools to use")
):
    """Investigate a security query using multiple tools."""
    async def _investigate():
        try:
            with Progress() as progress:
                task = progress.add_task("[cyan]Investigating...", total=100)
                
                # Initialize tools
                available_tools = {
                    "whois": WhoisTool(),
                    "shodan": ShodanTool(api_key=os.getenv("SHODAN_API_KEY"))
                }
                
                selected_tools = [
                    tool for name, tool in available_tools.items()
                    if name in tools
                ]
                
                # Create investigation agent
                agent = await agent_manager.create_agent(
                    agent_id="investigator",
                    agent_type="investigator",
                    tools=selected_tools
                )
                
                progress.update(task, advance=50)
                
                # Execute investigation
                result = await agent.execute_task(query)
                
                progress.update(task, advance=50)
                
                # Display results
                console.print("[green]Investigation Complete![/green]")
                console.print(result)
                
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
    
    asyncio.run(_investigate())


@app.command()
def list_agents():
    """List all available agents."""
    async def _list():
        try:
            agents = agent_manager.agents
            
            table = Table(show_header=True)
            table.add_column("Agent ID")
            table.add_column("Type")
            table.add_column("Status")
            
            for agent_id, agent in agents.items():
                table.add_row(
                    agent_id,
                    getattr(agent, "type", "unknown"),
                    "Active"
                )
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
    
    asyncio.run(_list())


if __name__ == "__main__":
    app()
