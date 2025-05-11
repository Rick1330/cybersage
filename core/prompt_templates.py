"""
Prompt Templates Module - Stores reusable prompt formats for CyberSage.

This module contains predefined prompt templates for various cybersecurity tasks,
agent interactions, and specialized security assessments with detailed context
handling and chain-of-thought reasoning.
"""

from typing import Dict, List
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.prompts.chat import SystemMessage, HumanMessage

# System message for establishing the AI security expert persona
SECURITY_EXPERT_SYSTEM_MSG = """You are CyberSage, an advanced AI cybersecurity expert with extensive knowledge in:
- Network security and penetration testing
- Vulnerability assessment and management
- Incident response and forensics
- Compliance and risk management
- Threat intelligence analysis
- Cloud security architecture

Always follow security best practices and ethical guidelines. Provide clear, actionable advice with proper risk assessment."""

# Template for security scanning tasks
SECURITY_SCAN_TEMPLATE = ChatPromptTemplate.from_messages([
    SystemMessage(content=SECURITY_EXPERT_SYSTEM_MSG),
    HumanMessage(content="""
    Perform a comprehensive {scan_type} security scan on target {target}.
    Scan Context: {context}
    Scope: {scope}

    Follow these steps:
    1. Pre-scan Validation:
       - Verify target is valid and within authorized scope
       - Check for potential impact on target systems
       - Validate scanning permissions and requirements

    2. Scan Configuration:
       - Select appropriate scanning tools and modules
       - Configure scan parameters for minimal impact
       - Set up logging and monitoring

    3. Execution Plan:
       - Detail the scanning methodology
       - List specific checks and tests to be performed
       - Define success criteria and stopping conditions

    4. Results Analysis:
       - Identify and categorize findings by severity
       - Correlate results with known vulnerabilities
       - Assess potential false positives

    5. Recommendations:
       - Prioritized remediation steps
       - Compensating controls if immediate fixes aren't possible
       - Long-term security improvements

    Please ensure all actions comply with security policies and regulations.
    """)
])

# Template for vulnerability assessment
VULNERABILITY_ASSESSMENT_TEMPLATE = ChatPromptTemplate.from_messages([
    SystemMessage(content=SECURITY_EXPERT_SYSTEM_MSG),
    HumanMessage(content="""
    Conduct a detailed vulnerability assessment based on the following:
    
    Target Environment: {environment}
    Asset Information: {assets}
    Previous Findings: {previous_findings}
    
    Provide analysis in the following format:

    1. Asset Inventory Analysis:
       - Critical assets identified
       - System dependencies
       - Access paths and exposure points

    2. Vulnerability Identification:
       - Known CVEs and exposures
       - Configuration weaknesses
       - Architecture vulnerabilities
       - Zero-day potential

    3. Risk Assessment:
       - Severity scoring (CVSS)
       - Exploit likelihood
       - Business impact
       - Attack complexity

    4. Remediation Planning:
       - Immediate actions required
       - Short-term mitigations
       - Long-term fixes
       - Resource requirements

    5. Defense-in-Depth Recommendations:
       - Additional security controls
       - Monitoring requirements
       - Policy updates needed
    """)
])

# Template for threat analysis with MITRE ATT&CK framework integration
THREAT_ANALYSIS_TEMPLATE = ChatPromptTemplate.from_messages([
    SystemMessage(content=SECURITY_EXPERT_SYSTEM_MSG),
    HumanMessage(content="""
    Analyze the following security data for advanced threats:
    
    Raw Data: {data}
    Context: {context}
    Time Period: {timeframe}
    
    Provide a comprehensive analysis:

    1. Initial Triage:
       - Severity assessment
       - Scope of potential compromise
       - Immediate response requirements

    2. Threat Actor Analysis:
       - TTPs identified
       - MITRE ATT&CK mapping
       - Known threat groups/campaigns
       - Motivation assessment

    3. Impact Analysis:
       - Affected systems/data
       - Business impact
       - Regulatory implications
       - Reputation risks

    4. Threat Intelligence:
       - IOC correlation
       - Similar incidents/campaigns
       - Industry-specific context
       - Emerging threat patterns

    5. Response Strategy:
       - Immediate containment steps
       - Investigation priorities
       - Evidence preservation
       - Stakeholder communication
    """)
])

# Template for log analysis with AI-enhanced pattern recognition
LOG_ANALYSIS_TEMPLATE = ChatPromptTemplate.from_messages([
    SystemMessage(content=SECURITY_EXPERT_SYSTEM_MSG),
    HumanMessage(content="""
    Analyze the following log data for security insights:
    
    Log Type: {log_type}
    Time Range: {timeframe}
    Log Data: {logs}
    Environment Context: {context}
    
    Provide detailed analysis:

    1. Log Summary:
       - Key events timeline
       - Traffic patterns
       - Access attempts
       - System changes

    2. Anomaly Detection:
       - Unusual patterns
       - Statistical deviations
       - Known IOCs
       - Behavioral anomalies

    3. Security Analysis:
       - Attack indicators
       - Policy violations
       - System vulnerabilities
       - Compliance issues

    4. Correlation Analysis:
       - Event relationships
       - Attack chain mapping
       - Root cause identification
       - Impact assessment

    5. Response Guidance:
       - Required investigations
       - Immediate actions
       - Monitoring adjustments
       - Process improvements
    """)
])

# Template for compliance assessment
COMPLIANCE_CHECK_TEMPLATE = ChatPromptTemplate.from_messages([
    SystemMessage(content=SECURITY_EXPERT_SYSTEM_MSG),
    HumanMessage(content="""
    Perform a compliance assessment for the following context:
    
    Framework: {framework}
    Scope: {scope}
    Current State: {current_state}
    Previous Audit Findings: {previous_findings}
    
    Provide a structured evaluation:

    1. Compliance Status:
       - Requirements mapping
       - Control effectiveness
       - Gap analysis
       - Risk levels

    2. Technical Controls:
       - Implementation status
       - Configuration review
       - Monitoring coverage
       - Documentation status

    3. Administrative Controls:
       - Policy alignment
       - Procedure adequacy
       - Training effectiveness
       - Record keeping

    4. Gap Remediation:
       - Priority findings
       - Required actions
       - Resource needs
       - Timeline estimates

    5. Continuous Compliance:
       - Monitoring requirements
       - Review schedules
       - Update processes
       - Audit preparation
    """)
])

# Template for incident response
INCIDENT_RESPONSE_TEMPLATE = ChatPromptTemplate.from_messages([
    SystemMessage(content=SECURITY_EXPERT_SYSTEM_MSG),
    HumanMessage(content="""
    Guide incident response for the following security incident:
    
    Incident Type: {incident_type}
    Severity: {severity}
    Current Status: {status}
    Available Data: {data}
    
    Provide response guidance:

    1. Incident Assessment:
       - Severity confirmation
       - Scope determination
       - Initial impact
       - Escalation needs

    2. Containment Strategy:
       - Immediate actions
       - System isolation
       - Access controls
       - Evidence preservation

    3. Investigation Steps:
       - Data collection
       - System analysis
       - Timeline creation
       - Attack reconstruction

    4. Recovery Planning:
       - Service restoration
       - Data recovery
       - System hardening
       - Monitoring enhancement

    5. Post-Incident:
       - Lessons learned
       - Process improvements
       - Documentation updates
       - Training needs
    """)
])

def get_specialized_template(template_type: str, **kwargs) -> PromptTemplate:
    """Get a specialized prompt template with custom parameters.
    
    Args:
        template_type: Type of template needed
        **kwargs: Additional template parameters
        
    Returns:
        Configured PromptTemplate instance
    """
    # Implementation for custom template generation
    pass
