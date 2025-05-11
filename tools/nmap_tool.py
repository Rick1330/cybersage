"""
Nmap Tool - Network scanning tool implementation.

This module provides a secure wrapper around the nmap network scanning tool.
"""

from typing import Dict, Any, List, Optional
import re
from .base_tool import BaseTool


class NmapTool(BaseTool):
    """Tool for performing network scans using nmap."""

    def __init__(
        self,
        timeout: int = 600,  # 10 minutes default for nmap
        dry_run: bool = False
    ):
        super().__init__(timeout=timeout, dry_run=dry_run)
        self.allowed_scan_types = {
            "basic": "-sS -T4",  # SYN scan
            "service": "-sV",    # Service detection
            "os": "-O",         # OS detection
            "script": "-sC",    # Default script scan
        }

    def validate_input(self, target: str, scan_type: str = "basic") -> bool:
        """Validate scan target and type."""
        # Validate IP address or hostname format
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$|^[\w\-\.]+$'
        if not re.match(ip_pattern, target):
            raise ValueError("Invalid target format")

        # Validate scan type
        if scan_type not in self.allowed_scan_types:
            raise ValueError(f"Invalid scan type. Allowed types: {list(self.allowed_scan_types.keys())}")

        return True

    async def execute(
        self,
        target: str,
        scan_type: str = "basic",
        ports: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute nmap scan with specified parameters.
        
        Args:
            target: IP address or hostname to scan
            scan_type: Type of scan to perform
            ports: Optional port specification (e.g., "80,443" or "1-1000")
            
        Returns:
            Dict containing scan results
        """
        self.validate_input(target=target, scan_type=scan_type)

        # Build command with proper escaping
        command = f"nmap {self.allowed_scan_types[scan_type]}"
        if ports:
            command += f" -p {ports}"
        command += f" {target}"

        # Execute scan
        result = await self._run_command(command)
        return self.sanitize_output(result)

    def sanitize_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from scan results."""
        # Remove any system-specific information
        if "stdout" in output:
            # Remove timing information and exact OS versions
            output["stdout"] = re.sub(
                r"OS details:.*\n",
                "OS details: [REDACTED]\n",
                output["stdout"]
            )
        return output
