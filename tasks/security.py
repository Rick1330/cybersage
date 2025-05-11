"""
Security-related scheduled tasks for CyberSage.

This module contains Celery tasks for automated security scanning,
threat intelligence updates, and vulnerability management.
"""

from celery import shared_task
from typing import List, Dict, Any
import asyncio
from datetime import datetime

from core.agent_manager import AgentManager
from services.openai_service import OpenAIService
from services.memory_service import MemoryService
from tools.nmap_tool import NmapTool
from tools.shodan_tool import ShodanTool


@shared_task
def run_vulnerability_scan(severity_levels: List[str]) -> Dict[str, Any]:
    """
    Run automated vulnerability scan for specified severity levels.
    
    Args:
        severity_levels: List of severity levels to scan for
    """
    async def _run_scan():
        try:
            # Initialize services and tools
            openai_service = OpenAIService()
            memory_service = MemoryService()
            agent_manager = AgentManager(openai_service, memory_service)
            
            nmap_tool = NmapTool()
            shodan_tool = ShodanTool()
            
            # Create security agent
            agent = await agent_manager.create_agent(
                agent_id=f"vuln_scan_{datetime.utcnow().isoformat()}",
                agent_type="security_scanner",
                tools=[nmap_tool, shodan_tool]
            )
            
            # Execute scan for each severity level
            results = {}
            for severity in severity_levels:
                scan_result = await agent.execute_task(
                    f"Perform vulnerability scan for {severity} severity issues"
                )
                results[severity] = scan_result
            
            return {
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat(),
                "results": results
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    return asyncio.run(_run_scan())


@shared_task
def update_threat_intel() -> Dict[str, Any]:
    """Update threat intelligence data from configured sources."""
    async def _update_intel():
        try:
            # Initialize services
            openai_service = OpenAIService()
            memory_service = MemoryService()
            agent_manager = AgentManager(openai_service, memory_service)
            
            # Create threat intel agent
            agent = await agent_manager.create_agent(
                agent_id=f"threat_intel_{datetime.utcnow().isoformat()}",
                agent_type="threat_intel",
                tools=[]  # Add threat intel tools when implemented
            )
            
            # Update threat data
            result = await agent.execute_task(
                "Update threat intelligence data from all sources"
            )
            
            return {
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat(),
                "result": result
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    return asyncio.run(_update_intel())
