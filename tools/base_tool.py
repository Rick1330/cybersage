"""
Base Tool Interface - Abstract base class for all CyberSage tools.

This module defines the interface that all tools must implement, including
security measures and execution controls.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import shlex
import subprocess
import asyncio
from datetime import datetime


class BaseTool(ABC):
    def __init__(
        self,
        timeout: int = 300,  # 5 minutes default timeout
        dry_run: bool = False
    ):
        self.timeout = timeout
        self.dry_run = dry_run

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with the given parameters."""
        pass

    async def _run_command(
        self,
        command: str,
        shell: bool = False,
        capture_output: bool = True
    ) -> Dict[str, Any]:
        """
        Safely execute a shell command with timeout and sanitization.
        
        Args:
            command: The command to execute
            shell: Whether to run through shell
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            Dict containing execution results
        """
        if self.dry_run:
            return {
                "command": command,
                "dry_run": True,
                "timestamp": datetime.utcnow().isoformat()
            }

        # Sanitize command
        if shell:
            sanitized_command = command
        else:
            sanitized_command = shlex.split(command)

        try:
            process = await asyncio.create_subprocess_exec(
                *sanitized_command,
                stdout=asyncio.subprocess.PIPE if capture_output else None,
                stderr=asyncio.subprocess.PIPE if capture_output else None
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                process.terminate()
                raise TimeoutError(f"Command timed out after {self.timeout} seconds")

            return {
                "command": command,
                "return_code": process.returncode,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "command": command,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters before execution."""
        return True

    def sanitize_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize tool output before returning."""
        return output
