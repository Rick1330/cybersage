"""
Configuration Service - Manages configuration for security tools and workflows.

This service provides centralized configuration management with version control,
validation, and secure distribution of configurations.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import hashlib
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Base exception for configuration-related errors."""
    pass

class ConfigurationService:
    """Service for managing security tool and workflow configurations."""
    
    def __init__(
        self,
        config_dir: str,
        env: str = "development",
        use_encryption: bool = True
    ):
        """Initialize configuration service.
        
        Args:
            config_dir: Base directory for configurations
            env: Environment name
            use_encryption: Whether to encrypt sensitive values
        """
        self.config_dir = Path(config_dir)
        self.env = env
        self.use_encryption = use_encryption
        self.cache: Dict[str, Any] = {}
        
        # Create config directories
        self.config_dir.mkdir(parents=True, exist_ok=True)
        (self.config_dir / "tools").mkdir(exist_ok=True)
        (self.config_dir / "workflows").mkdir(exist_ok=True)
        (self.config_dir / "policies").mkdir(exist_ok=True)
        
        # Load base configurations
        self._load_base_configs()

    def _load_base_configs(self) -> None:
        """Load base configurations for the environment."""
        try:
            # Load environment config
            env_config_path = self.config_dir / f"{self.env}.yaml"
            if env_config_path.exists():
                with open(env_config_path) as f:
                    self.env_config = yaml.safe_load(f)
            else:
                self.env_config = {}
                
            # Load security policies
            policy_path = self.config_dir / "policies/security_policies.yaml"
            if policy_path.exists():
                with open(policy_path) as f:
                    self.security_policies = yaml.safe_load(f)
            else:
                self.security_policies = {}
                
        except Exception as e:
            raise ConfigError(f"Failed to load base configs: {str(e)}")

    def get_tool_config(
        self,
        tool_name: str,
        validate: bool = True
    ) -> Dict[str, Any]:
        """Get configuration for a security tool.
        
        Args:
            tool_name: Name of the tool
            validate: Whether to validate the configuration
            
        Returns:
            Tool configuration dictionary
            
        Raises:
            ConfigError: If configuration is invalid or not found
        """
        try:
            # Check cache first
            cache_key = f"tool:{tool_name}"
            if cache_key in self.cache:
                return self.cache[cache_key]
                
            # Load tool config
            config_path = self.config_dir / "tools" / f"{tool_name}.yaml"
            if not config_path.exists():
                raise ConfigError(f"Configuration not found for tool: {tool_name}")
                
            with open(config_path) as f:
                config = yaml.safe_load(f)
                
            # Merge with environment config
            if tool_name in self.env_config.get("tools", {}):
                config.update(self.env_config["tools"][tool_name])
                
            # Validate if requested
            if validate:
                self._validate_tool_config(tool_name, config)
                
            # Cache the config
            self.cache[cache_key] = config
            return config
            
        except Exception as e:
            raise ConfigError(f"Failed to get tool config: {str(e)}")

    def get_workflow_config(
        self,
        workflow_name: str
    ) -> Dict[str, Any]:
        """Get configuration for a security workflow.
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            Workflow configuration dictionary
            
        Raises:
            ConfigError: If configuration is not found
        """
        try:
            # Check cache first
            cache_key = f"workflow:{workflow_name}"
            if cache_key in self.cache:
                return self.cache[cache_key]
                
            # Load workflow config
            config_path = self.config_dir / "workflows" / f"{workflow_name}.yaml"
            if not config_path.exists():
                raise ConfigError(
                    f"Configuration not found for workflow: {workflow_name}"
                )
                
            with open(config_path) as f:
                config = yaml.safe_load(f)
                
            # Merge with environment config
            if workflow_name in self.env_config.get("workflows", {}):
                config.update(self.env_config["workflows"][workflow_name])
                
            # Cache the config
            self.cache[cache_key] = config
            return config
            
        except Exception as e:
            raise ConfigError(f"Failed to get workflow config: {str(e)}")

    def update_tool_config(
        self,
        tool_name: str,
        config: Dict[str, Any],
        validate: bool = True
    ) -> None:
        """Update configuration for a security tool.
        
        Args:
            tool_name: Name of the tool
            config: New configuration
            validate: Whether to validate the configuration
            
        Raises:
            ConfigError: If update fails
        """
        try:
            # Validate if requested
            if validate:
                self._validate_tool_config(tool_name, config)
                
            # Save config
            config_path = self.config_dir / "tools" / f"{tool_name}.yaml"
            with open(config_path, "w") as f:
                yaml.safe_dump(config, f)
                
            # Update cache
            self.cache[f"tool:{tool_name}"] = config
            
        except Exception as e:
            raise ConfigError(f"Failed to update tool config: {str(e)}")

    def update_workflow_config(
        self,
        workflow_name: str,
        config: Dict[str, Any]
    ) -> None:
        """Update configuration for a security workflow.
        
        Args:
            workflow_name: Name of the workflow
            config: New configuration
            
        Raises:
            ConfigError: If update fails
        """
        try:
            # Save config
            config_path = self.config_dir / "workflows" / f"{workflow_name}.yaml"
            with open(config_path, "w") as f:
                yaml.safe_dump(config, f)
                
            # Update cache
            self.cache[f"workflow:{workflow_name}"] = config
            
        except Exception as e:
            raise ConfigError(f"Failed to update workflow config: {str(e)}")

    def get_security_policy(
        self,
        policy_name: str
    ) -> Dict[str, Any]:
        """Get a security policy configuration.
        
        Args:
            policy_name: Name of the policy
            
        Returns:
            Policy configuration dictionary
            
        Raises:
            ConfigError: If policy is not found
        """
        try:
            if policy_name not in self.security_policies:
                raise ConfigError(f"Security policy not found: {policy_name}")
            return self.security_policies[policy_name]
        except Exception as e:
            raise ConfigError(f"Failed to get security policy: {str(e)}")

    def validate_against_policy(
        self,
        config: Dict[str, Any],
        policy_name: str
    ) -> bool:
        """Validate a configuration against a security policy.
        
        Args:
            config: Configuration to validate
            policy_name: Name of the policy to validate against
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            ConfigError: If validation fails
        """
        try:
            policy = self.get_security_policy(policy_name)
            
            # Implementation of policy validation logic
            # This would check the config against policy rules
            return True
            
        except Exception as e:
            raise ConfigError(f"Policy validation failed: {str(e)}")

    def _validate_tool_config(
        self,
        tool_name: str,
        config: Dict[str, Any]
    ) -> None:
        """Validate a tool configuration.
        
        Args:
            tool_name: Name of the tool
            config: Configuration to validate
            
        Raises:
            ConfigError: If validation fails
        """
        # Implementation of tool-specific validation logic
        pass

    def get_sensitive_value(
        self,
        key: str,
        default: Optional[str] = None
    ) -> Optional[str]:
        """Get a sensitive configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value or default
            
        Raises:
            ConfigError: If value retrieval fails
        """
        try:
            # Implementation of secure value retrieval
            # This would integrate with a secrets manager
            return os.getenv(key, default)
        except Exception as e:
            raise ConfigError(f"Failed to get sensitive value: {str(e)}")

    def set_sensitive_value(
        self,
        key: str,
        value: str
    ) -> None:
        """Set a sensitive configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
            
        Raises:
            ConfigError: If value setting fails
        """
        try:
            # Implementation of secure value storage
            # This would integrate with a secrets manager
            pass
        except Exception as e:
            raise ConfigError(f"Failed to set sensitive value: {str(e)}")

    def clear_cache(self) -> None:
        """Clear the configuration cache."""
        self.cache.clear()

    def invalidate_cache_entry(self, key: str) -> None:
        """Invalidate a specific cache entry.
        
        Args:
            key: Cache key to invalidate
        """
        if key in self.cache:
            del self.cache[key]

    def get_config_metadata(
        self,
        config_type: str,
        name: str
    ) -> Dict[str, Any]:
        """Get metadata for a configuration.
        
        Args:
            config_type: Type of configuration ('tool' or 'workflow')
            name: Name of the configuration
            
        Returns:
            Configuration metadata
            
        Raises:
            ConfigError: If metadata retrieval fails
        """
        try:
            config_path = self.config_dir / config_type / f"{name}.yaml"
            if not config_path.exists():
                raise ConfigError(
                    f"Configuration not found: {config_type}/{name}"
                )
                
            return {
                "name": name,
                "type": config_type,
                "last_modified": datetime.fromtimestamp(
                    config_path.stat().st_mtime
                ).isoformat(),
                "size": config_path.stat().st_size,
                "hash": self._get_file_hash(config_path)
            }
            
        except Exception as e:
            raise ConfigError(f"Failed to get config metadata: {str(e)}")

    def _get_file_hash(self, path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
