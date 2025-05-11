"""
Shodan Tool - Interface to Shodan API for internet-wide scanning data.

This module provides a secure wrapper around the Shodan API for gathering
information about internet-connected devices.
"""

from typing import Dict, Any, Optional, List
import shodan
from datetime import datetime
from .base_tool import BaseTool


class ShodanTool(BaseTool):
    """Tool for interacting with Shodan API."""
    
    def __init__(
        self,
        api_key: str,
        timeout: int = 300,
        dry_run: bool = False
    ):
        super().__init__(timeout=timeout, dry_run=dry_run)
        self.api = shodan.Shodan(api_key)
        
    def validate_input(self, query: str) -> bool:
        """Validate Shodan search query."""
        if not query or len(query) < 3:
            raise ValueError("Query too short or empty")
        
        # Check for potentially dangerous queries
        dangerous_terms = ['malware', 'botnet', 'ransomware']
        for term in dangerous_terms:
            if term in query.lower():
                raise ValueError(f"Query contains prohibited term: {term}")
                
        return True

    async def execute(
        self,
        query: str,
        limit: int = 100,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute Shodan search query.
        
        Args:
            query: Shodan search query
            limit: Maximum number of results to return
            
        Returns:
            Dict containing search results
        """
        self.validate_input(query)
        
        try:
            if self.dry_run:
                return {
                    "query": query,
                    "dry_run": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            results = self.api.search(query, limit=limit)
            
            processed_results = {
                "total": results['total'],
                "matches": [
                    self._process_match(match)
                    for match in results['matches'][:limit]
                ],
                "query": query,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return self.sanitize_output(processed_results)
            
        except shodan.APIError as e:
            return {
                "error": str(e),
                "query": query,
                "timestamp": datetime.utcnow().isoformat()
            }

    def _process_match(self, match: Dict[str, Any]) -> Dict[str, Any]:
        """Process and structure a single Shodan result match."""
        return {
            "ip": match.get('ip_str'),
            "port": match.get('port'),
            "hostnames": match.get('hostnames', []),
            "organization": match.get('org'),
            "location": {
                "country": match.get('location', {}).get('country_name'),
                "city": match.get('location', {}).get('city'),
            },
            "last_update": match.get('last_update'),
            "services": {
                "product": match.get('product', ''),
                "version": match.get('version', ''),
                "cpe": match.get('cpe', [])
            }
        }

    def sanitize_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from Shodan results."""
        # Remove internal network information
        if 'matches' in output:
            for match in output['matches']:
                if 'data' in match:
                    del match['data']  # Remove raw banner data
                if 'ip_str' in match and self._is_internal_ip(match['ip_str']):
                    match['ip_str'] = '[REDACTED-INTERNAL]'
                    
        return output
        
    def _is_internal_ip(self, ip: str) -> bool:
        """Check if an IP address is internal."""
        internal_prefixes = [
            '10.',
            '172.16.', '172.17.', '172.18.', '172.19.',
            '172.20.', '172.21.', '172.22.', '172.23.',
            '172.24.', '172.25.', '172.26.', '172.27.',
            '172.28.', '172.29.', '172.30.', '172.31.',
            '192.168.'
        ]
        return any(ip.startswith(prefix) for prefix in internal_prefixes)
