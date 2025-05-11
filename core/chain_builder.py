"""
Chain Builder Module - Assembles LangChain chains for CyberSage.

This module provides factory methods to create and configure different types of
LangChain chains for various cybersecurity tasks with support for sequential
chains, multi-step reasoning, and tool integration.
"""

import logging
from typing import List, Optional, Dict, Any, Union
from langchain.chains import LLMChain, SequentialChain
from langchain.chains.base import Chain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import AsyncCallbackManager
from langchain.prompts import PromptTemplate
from core.prompt_templates import (
    SECURITY_SCAN_TEMPLATE,
    THREAT_ANALYSIS_TEMPLATE,
    LOG_ANALYSIS_TEMPLATE,
    VULNERABILITY_ASSESSMENT_TEMPLATE,
    INCIDENT_RESPONSE_TEMPLATE,
    COMPLIANCE_CHECK_TEMPLATE
)

logger = logging.getLogger(__name__)

class ChainBuilderError(Exception):
    """Base exception for chain builder related errors."""
    pass

class ChainBuilder:
    def __init__(
        self,
        llm,
        memory_service,
        vectorstore_service=None,
        callback_manager: Optional[AsyncCallbackManager] = None
    ):
        """Initialize the chain builder.
        
        Args:
            llm: Language model instance
            memory_service: Memory service instance
            vectorstore_service: Optional vector store service
            callback_manager: Optional callback manager for chain events
        """
        self.llm = llm
        self.memory_service = memory_service
        self.vectorstore_service = vectorstore_service
        self.callback_manager = callback_manager

    async def _create_base_chain(
        self,
        prompt_template: Union[str, PromptTemplate],
        memory_key: Optional[str] = None,
        output_key: Optional[str] = None,
        **kwargs
    ) -> LLMChain:
        """Create a base LLMChain with common configuration.
        
        Args:
            prompt_template: String template or PromptTemplate instance
            memory_key: Optional memory key for conversation history
            output_key: Optional key for chain output
            **kwargs: Additional chain configuration
            
        Returns:
            Configured LLMChain instance
            
        Raises:
            ChainBuilderError: If chain creation fails
        """
        try:
            # Create memory if key provided
            memory = await self.memory_service.create_memory(memory_key) if memory_key else None
            
            # Convert string template to PromptTemplate if needed
            if isinstance(prompt_template, str):
                prompt_template = PromptTemplate(
                    template=prompt_template,
                    input_variables=["input"]
                )
            
            return LLMChain(
                llm=self.llm,
                prompt=prompt_template,
                memory=memory,
                output_key=output_key,
                callback_manager=self.callback_manager,
                verbose=True,
                **kwargs
            )
        except Exception as e:
            logger.error(f"Failed to create base chain: {str(e)}")
            raise ChainBuilderError(f"Base chain creation failed: {str(e)}") from e

    async def build_security_scan_chain(
        self,
        memory_key: Optional[str] = None,
        include_vulnerability_check: bool = True,
        include_compliance_check: bool = False
    ) -> Chain:
        """Build a chain for security scanning tasks.
        
        Args:
            memory_key: Optional memory key
            include_vulnerability_check: Whether to include vulnerability scanning
            include_compliance_check: Whether to include compliance checking
            
        Returns:
            Chain instance
            
        Raises:
            ChainBuilderError: If chain building fails
        """
        try:
            chains = []
            
            # Base security scan
            scan_chain = await self._create_base_chain(
                SECURITY_SCAN_TEMPLATE,
                memory_key=memory_key,
                output_key="scan_results"
            )
            chains.append(scan_chain)
            
            # Optional vulnerability check
            if include_vulnerability_check:
                vuln_chain = await self._create_base_chain(
                    VULNERABILITY_ASSESSMENT_TEMPLATE,
                    output_key="vulnerability_results"
                )
                chains.append(vuln_chain)
            
            # Optional compliance check
            if include_compliance_check:
                compliance_chain = await self._create_base_chain(
                    COMPLIANCE_CHECK_TEMPLATE,
                    output_key="compliance_results"
                )
                chains.append(compliance_chain)
            
            # Return single chain if only one, otherwise sequential
            if len(chains) == 1:
                return chains[0]
                
            return SequentialChain(
                chains=chains,
                input_variables=["input"],
                output_variables=[chain.output_key for chain in chains],
                verbose=True
            )
            
        except Exception as e:
            logger.error(f"Failed to build security scan chain: {str(e)}")
            raise ChainBuilderError(f"Security scan chain building failed: {str(e)}") from e

    async def build_threat_analysis_chain(
        self,
        memory_key: Optional[str] = None,
        use_vector_store: bool = True
    ) -> Chain:
        """Build a chain for threat analysis tasks.
        
        Args:
            memory_key: Optional memory key
            use_vector_store: Whether to use vector store for context
            
        Returns:
            Chain instance
        """
        try:
            # Base threat analysis chain
            chain = await self._create_base_chain(
                THREAT_ANALYSIS_TEMPLATE,
                memory_key=memory_key,
                output_key="threat_analysis"
            )
            
            # Add vector store retrieval if requested
            if use_vector_store and self.vectorstore_service:
                chain = self._add_vector_store_retrieval(
                    chain,
                    "threat_intelligence"
                )
                
            return chain
            
        except Exception as e:
            logger.error(f"Failed to build threat analysis chain: {str(e)}")
            raise ChainBuilderError(f"Threat analysis chain building failed: {str(e)}") from e

    async def build_log_analysis_chain(
        self,
        memory_key: Optional[str] = None,
        log_type: Optional[str] = None
    ) -> Chain:
        """Build a chain for log analysis tasks.
        
        Args:
            memory_key: Optional memory key
            log_type: Optional log type for specialized analysis
            
        Returns:
            Chain instance
        """
        try:
            template = LOG_ANALYSIS_TEMPLATE
            
            # Customize template based on log type if needed
            if log_type:
                template = self._get_specialized_log_template(log_type)
                
            return await self._create_base_chain(
                template,
                memory_key=memory_key,
                output_key="log_analysis"
            )
            
        except Exception as e:
            logger.error(f"Failed to build log analysis chain: {str(e)}")
            raise ChainBuilderError(f"Log analysis chain building failed: {str(e)}") from e

    async def build_incident_response_chain(
        self,
        memory_key: Optional[str] = None,
        severity_level: str = "medium"
    ) -> Chain:
        """Build a chain for incident response tasks.
        
        Args:
            memory_key: Optional memory key
            severity_level: Incident severity level
            
        Returns:
            Chain instance
        """
        try:
            chains = []
            
            # Initial incident assessment
            assessment_chain = await self._create_base_chain(
                INCIDENT_RESPONSE_TEMPLATE,
                memory_key=memory_key,
                output_key="incident_assessment"
            )
            chains.append(assessment_chain)
            
            # Add severity-specific handling
            if severity_level in ["high", "critical"]:
                mitigation_chain = await self._create_base_chain(
                    self._get_severity_template(severity_level),
                    output_key="mitigation_steps"
                )
                chains.append(mitigation_chain)
            
            return SequentialChain(
                chains=chains,
                input_variables=["input"],
                output_variables=[chain.output_key for chain in chains],
                verbose=True
            )
            
        except Exception as e:
            logger.error(f"Failed to build incident response chain: {str(e)}")
            raise ChainBuilderError(f"Incident response chain building failed: {str(e)}") from e

    def _add_vector_store_retrieval(
        self,
        chain: Chain,
        retrieval_key: str
    ) -> Chain:
        """Add vector store retrieval to a chain.
        
        Args:
            chain: Base chain to enhance
            retrieval_key: Key for retrieved context
            
        Returns:
            Enhanced chain with vector store retrieval
        """
        if not self.vectorstore_service:
            logger.warning("Vector store service not available")
            return chain
            
        # Implementation depends on specific needs
        # This is a placeholder for the actual implementation
        return chain

    def _get_specialized_log_template(self, log_type: str) -> PromptTemplate:
        """Get specialized template for specific log types.
        
        Args:
            log_type: Type of log
            
        Returns:
            Appropriate PromptTemplate
        """
        # Add specialized templates as needed
        templates = {
            "network": "Network log analysis template",
            "system": "System log analysis template",
            "application": "Application log analysis template"
        }
        
        template_text = templates.get(log_type, LOG_ANALYSIS_TEMPLATE)
        return PromptTemplate(
            template=template_text,
            input_variables=["input"]
        )

    def _get_severity_template(self, severity: str) -> PromptTemplate:
        """Get template based on incident severity.
        
        Args:
            severity: Severity level
            
        Returns:
            Appropriate PromptTemplate
        """
        # Add specialized templates for different severity levels
        templates = {
            "critical": "Critical incident response template",
            "high": "High severity incident response template"
        }
        
        template_text = templates.get(severity, INCIDENT_RESPONSE_TEMPLATE)
        return PromptTemplate(
            template=template_text,
            input_variables=["input"]
        )
