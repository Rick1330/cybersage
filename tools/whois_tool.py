"""
WHOIS Tool - Domain and IP WHOIS information lookup tool.

This module provides a secure wrapper around whois lookups for domains and IP addresses.
"""

from typing import Dict, Any, Optional
import re
import whois
from .base_tool import BaseTool


class WhoisTool(BaseTool):
    """Tool for performing WHOIS lookups."""

    def validate_input(self, target: str) -> bool:
        """Validate the target domain or IP."""
        # Domain pattern
        domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        # IPv4 pattern
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        
        if not (re.match(domain_pattern, target) or re.match(ip_pattern, target)):
            raise ValueError("Invalid domain or IP format")
        
        return True

    async def execute(
        self,
        target: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute WHOIS lookup for a domain or IP.
        
        Args:
            target: Domain name or IP address to lookup
            
        Returns:
            Dict containing WHOIS information
        """
        self.validate_input(target)
        
        try:
            whois_info = whois.whois(target)
            
            # Clean and structure the response
            result = {
                "domain_name": whois_info.domain_name,
                "registrar": whois_info.registrar,
                "creation_date": whois_info.creation_date,
                "expiration_date": whois_info.expiration_date,
                "last_updated": whois_info.updated_date,
                "status": whois_info.status,
                "name_servers": whois_info.name_servers,
                "emails": whois_info.emails,
            }
            
            return self.sanitize_output(result)
            
        except Exception as e:
            return {
                "error": str(e),
                "target": target,
                "timestamp": datetime.utcnow().isoformat()
            }

    def sanitize_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from WHOIS results."""
        # Remove personal information if present
        sensitive_fields = ['registrant_name', 'admin_name', 'tech_name']
        for field in sensitive_fields:
            if field in output:
                output[field] = '[REDACTED]'
                
        return output
