"""
VirusTotal Tool - Threat intelligence gathering through VirusTotal API.

This module provides a secure wrapper around the VirusTotal API for gathering
malware analysis, file reputation, and threat intelligence data.
"""

from typing import Dict, Any, List, Optional, Union
import os
import hashlib
import aiohttp
from datetime import datetime, timedelta
from .base_tool import BaseTool

class VirusTotalError(Exception):
    """Base exception for VirusTotal-related errors."""
    pass

class VirusTotalTool(BaseTool):
    """Tool for interacting with VirusTotal API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 60,
        dry_run: bool = False,
        cache_ttl: int = 3600  # 1 hour cache
    ):
        """Initialize VirusTotal tool.
        
        Args:
            api_key: VirusTotal API key (optional, will look for VT_API_KEY env var)
            timeout: API request timeout in seconds
            dry_run: Whether to run in dry-run mode
            cache_ttl: Cache time-to-live in seconds
        """
        super().__init__(timeout=timeout, dry_run=dry_run)
        self.api_key = api_key or os.getenv("VT_API_KEY")
        if not self.api_key:
            raise VirusTotalError("VirusTotal API key not provided")
            
        self.api_url = "https://www.virustotal.com/vtapi/v2"
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}

    def validate_input(self, resource: str, resource_type: str) -> bool:
        """Validate input parameters.
        
        Args:
            resource: Resource to analyze (hash, URL, domain, IP)
            resource_type: Type of resource ('file', 'url', 'domain', 'ip')
        """
        if not resource:
            raise ValueError("Resource cannot be empty")
            
        if resource_type not in ['file', 'url', 'domain', 'ip']:
            raise ValueError("Invalid resource type")
            
        # Validate format based on type
        if resource_type == 'file':
            # Validate MD5, SHA-1, or SHA-256 hash format
            if not all(c in '0123456789abcdefABCDEF' for c in resource):
                raise ValueError("Invalid hash format")
        elif resource_type == 'url':
            # Basic URL validation
            if not resource.startswith(('http://', 'https://')):
                raise ValueError("Invalid URL format")
        elif resource_type == 'ip':
            # Basic IP validation
            parts = resource.split('.')
            if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
                raise ValueError("Invalid IP format")
                
        return True

    def _is_cached_result_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid."""
        if cache_key not in self._cache:
            return False
            
        cache_time = datetime.fromisoformat(self._cache[cache_key]["timestamp"])
        age = (datetime.utcnow() - cache_time).total_seconds()
        
        return age < self.cache_ttl

    async def execute(
        self,
        resource: str,
        resource_type: str,
        refresh_cache: bool = False
    ) -> Dict[str, Any]:
        """
        Execute VirusTotal API query.
        
        Args:
            resource: Resource to analyze (hash, URL, domain, IP)
            resource_type: Type of resource ('file', 'url', 'domain', 'ip')
            refresh_cache: Whether to force a cache refresh
            
        Returns:
            Dict containing analysis results
            
        Raises:
            VirusTotalError: If query fails
        """
        try:
            self.validate_input(resource, resource_type)
            
            cache_key = f"{resource_type}:{resource}"
            
            # Check cache first
            if not refresh_cache and self._is_cached_result_valid(cache_key):
                return self._cache[cache_key]

            # Prepare API endpoint and parameters
            if resource_type == 'file':
                endpoint = f"{self.api_url}/file/report"
            elif resource_type == 'url':
                endpoint = f"{self.api_url}/url/report"
            elif resource_type == 'domain':
                endpoint = f"{self.api_url}/domain/report"
            else:  # ip
                endpoint = f"{self.api_url}/ip-address/report"

            params = {
                'apikey': self.api_key,
                'resource': resource
            }

            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint,
                    params=params,
                    timeout=self.timeout
                ) as response:
                    if response.status != 200:
                        raise VirusTotalError(
                            f"API request failed with status {response.status}"
                        )
                    data = await response.json()

            # Process and cache result
            result = self._process_result(data, resource_type)
            processed_result = self.sanitize_output(result)
            self._cache[cache_key] = processed_result
            
            return processed_result
            
        except aiohttp.ClientError as e:
            raise VirusTotalError(f"HTTP request failed: {str(e)}")
        except Exception as e:
            raise VirusTotalError(f"Unexpected error: {str(e)}")

    def _process_result(
        self,
        data: Dict[str, Any],
        resource_type: str
    ) -> Dict[str, Any]:
        """Process and structure API response."""
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "resource_type": resource_type,
            "analysis": {}
        }

        if resource_type == 'file':
            result["analysis"] = {
                "positives": data.get("positives", 0),
                "total": data.get("total", 0),
                "scan_date": data.get("scan_date"),
                "sha256": data.get("sha256"),
                "md5": data.get("md5"),
                "scans": self._process_scans(data.get("scans", {}))
            }
        elif resource_type == 'url':
            result["analysis"] = {
                "url": data.get("url"),
                "positives": data.get("positives", 0),
                "total": data.get("total", 0),
                "scan_date": data.get("scan_date"),
                "scans": self._process_scans(data.get("scans", {}))
            }
        elif resource_type in ['domain', 'ip']:
            result["analysis"] = {
                "resolutions": data.get("resolutions", []),
                "detected_urls": self._process_detected_urls(
                    data.get("detected_urls", [])
                ),
                "detected_downloaded_samples": data.get(
                    "detected_downloaded_samples",
                    []
                ),
                "whois": data.get("whois"),
                "response_code": data.get("response_code")
            }

        return result

    def _process_scans(
        self,
        scans: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Process scan results from different antivirus engines."""
        processed_scans = {}
        for engine, results in scans.items():
            processed_scans[engine] = {
                "detected": results.get("detected", False),
                "result": results.get("result"),
                "update": results.get("update")
            }
        return processed_scans

    def _process_detected_urls(
        self,
        detected_urls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process detected malicious URLs."""
        return [
            {
                "url": url.get("url"),
                "positives": url.get("positives", 0),
                "total": url.get("total", 0),
                "scan_date": url.get("scan_date")
            }
            for url in detected_urls
        ]

    def sanitize_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from VirusTotal results."""
        # Remove API key if present
        if "apikey" in output:
            del output["apikey"]
            
        # Remove internal URLs if present
        if "analysis" in output and "detected_urls" in output["analysis"]:
            output["analysis"]["detected_urls"] = [
                url for url in output["analysis"]["detected_urls"]
                if not self._is_internal_url(url.get("url", ""))
            ]
            
        return output

    def _is_internal_url(self, url: str) -> bool:
        """Check if a URL points to an internal resource."""
        internal_indicators = [
            "internal", "intranet", "local", "localhost",
            "127.0.0.1", "192.168.", "10.", "172.16."
        ]
        return any(indicator in url.lower() for indicator in internal_indicators)

    async def scan_file(
        self,
        file_path: str,
        wait_for_completion: bool = False
    ) -> Dict[str, Any]:
        """
        Submit a file for scanning.
        
        Args:
            file_path: Path to file to scan
            wait_for_completion: Whether to wait for scan completion
            
        Returns:
            Dict containing scan results
            
        Raises:
            VirusTotalError: If scan fails
        """
        try:
            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            # Check if we have a cached result
            cache_key = f"file:{file_hash}"
            if self._is_cached_result_valid(cache_key):
                return self._cache[cache_key]

            # Submit file for scanning
            # Implementation for file upload
            pass
            
        except Exception as e:
            raise VirusTotalError(f"File scan failed: {str(e)}")

    async def get_file_behavior(self, file_hash: str) -> Dict[str, Any]:
        """
        Get behavioral analysis of a file.
        
        Args:
            file_hash: SHA-256 hash of the file
            
        Returns:
            Dict containing behavioral analysis
            
        Raises:
            VirusTotalError: If retrieval fails
        """
        try:
            endpoint = f"{self.api_url}/file/behaviour"
            params = {
                'apikey': self.api_key,
                'hash': file_hash
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint,
                    params=params,
                    timeout=self.timeout
                ) as response:
                    if response.status != 200:
                        raise VirusTotalError(
                            f"API request failed with status {response.status}"
                        )
                    data = await response.json()

            return self.sanitize_output({
                "hash": file_hash,
                "timestamp": datetime.utcnow().isoformat(),
                "behavior": {
                    "processes": data.get("processes", []),
                    "network": data.get("network", {}),
                    "files": data.get("files", []),
                    "registry": data.get("registry", [])
                }
            })
            
        except Exception as e:
            raise VirusTotalError(f"Failed to get file behavior: {str(e)}")
