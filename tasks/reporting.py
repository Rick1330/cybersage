"""
Reporting tasks for CyberSage.

This module contains Celery tasks for generating various security reports
and analytics summaries.
"""

from celery import shared_task
from typing import Dict, Any
import asyncio
from datetime import datetime, timedelta
import jinja2
import weasyprint

from core.agent_manager import AgentManager
from services.openai_service import OpenAIService
from services.memory_service import MemoryService


@shared_task
def generate_security_report() -> Dict[str, Any]:
    """Generate weekly security report with insights and recommendations."""
    async def _generate_report():
        try:
            # Initialize services
            openai_service = OpenAIService()
            memory_service = MemoryService()
            agent_manager = AgentManager(openai_service, memory_service)
            
            # Create reporting agent
            agent = await agent_manager.create_agent(
                agent_id=f"report_gen_{datetime.utcnow().isoformat()}",
                agent_type="report_generator",
                tools=[]
            )
            
            # Generate report content
            report_data = await agent.execute_task(
                "Generate comprehensive security report for the past week"
            )
            
            # Create PDF report
            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader('templates/reports')
            )
            template = env.get_template('security_report.html')
            html_content = template.render(
                report=report_data,
                generated_at=datetime.utcnow()
            )
            
            # Save PDF
            report_path = f"reports/security_report_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
            weasyprint.HTML(string=html_content).write_pdf(report_path)
            
            return {
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat(),
                "report_path": report_path
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    return asyncio.run(_generate_report())


@shared_task
def generate_threat_summary() -> Dict[str, Any]:
    """Generate daily threat intelligence summary."""
    async def _generate_summary():
        try:
            # Initialize services
            openai_service = OpenAIService()
            memory_service = MemoryService()
            agent_manager = AgentManager(openai_service, memory_service)
            
            # Create summary agent
            agent = await agent_manager.create_agent(
                agent_id=f"threat_summary_{datetime.utcnow().isoformat()}",
                agent_type="threat_analyzer",
                tools=[]
            )
            
            # Generate summary
            summary = await agent.execute_task(
                "Generate threat intelligence summary for the past 24 hours"
            )
            
            return {
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat(),
                "summary": summary
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    return asyncio.run(_generate_summary())
