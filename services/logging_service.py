"""
Logging Service - Centralized logging configuration and management.

This service provides structured logging with various outputs and formats,
including file rotation, remote logging support, and specialized handling
for security events and audit logging.
"""

import json
import logging
import logging.handlers
from typing import Optional, Dict, Any, Union
from pathlib import Path
import yaml
from datetime import datetime
import hashlib
import uuid
from enum import Enum

class SecurityEventType(Enum):
    """Types of security events that can be logged."""
    ACCESS_ATTEMPT = "access_attempt"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_ALERT = "security_alert"
    POLICY_VIOLATION = "policy_violation"
    SYSTEM_CHANGE = "system_change"
    USER_ACTION = "user_action"
    API_CALL = "api_call"
    DATA_ACCESS = "data_access"

class LoggingError(Exception):
    """Base exception for logging service related errors."""
    pass

class LoggingService:
    def __init__(
        self,
        config_path: str,
        log_dir: str = "logs",
        app_name: str = "cybersage",
        enable_audit_log: bool = True,
        enable_security_log: bool = True
    ):
        """Initialize the logging service.
        
        Args:
            config_path: Path to logging configuration file
            log_dir: Directory for log files
            app_name: Application name
            enable_audit_log: Whether to enable audit logging
            enable_security_log: Whether to enable security event logging
        """
        self.config_path = config_path
        self.log_dir = Path(log_dir)
        self.app_name = app_name
        self.enable_audit_log = enable_audit_log
        self.enable_security_log = enable_security_log
        
        # Create log directories
        self.log_dir.mkdir(exist_ok=True)
        (self.log_dir / "audit").mkdir(exist_ok=True)
        (self.log_dir / "security").mkdir(exist_ok=True)
        
        # Load logging configuration
        self.setup_logging()
        
        # Special loggers
        self.audit_logger = self._setup_audit_logger()
        self.security_logger = self._setup_security_logger()

    def setup_logging(self) -> None:
        """Set up logging configuration from YAML file.
        
        Raises:
            LoggingError: If logging setup fails
        """
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)

            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(config.get('root_level', 'INFO'))

            # Main application log
            app_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / f"{self.app_name}.log",
                maxBytes=10485760,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            app_handler.setFormatter(logging.Formatter(
                config.get('file_format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ))
            root_logger.addHandler(app_handler)

            # Console handler for development
            if config.get('enable_console', True):
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(logging.Formatter(
                    config.get('console_format', '%(levelname)s: %(message)s')
                ))
                root_logger.addHandler(console_handler)

            # Optional integrations
            self._setup_integrations(config)

        except Exception as e:
            raise LoggingError(f"Failed to set up logging: {str(e)}") from e

    def _setup_audit_logger(self) -> logging.Logger:
        """Set up specialized audit logger.
        
        Returns:
            Configured audit logger
        """
        if not self.enable_audit_log:
            return logging.getLogger('audit_disabled')
            
        audit_logger = logging.getLogger('audit')
        audit_logger.setLevel(logging.INFO)
        audit_logger.propagate = False
        
        handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "audit" / "audit.log",
            maxBytes=52428800,  # 50MB
            backupCount=10,
            encoding='utf-8'
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(event_id)s] - %(message)s'
        )
        handler.setFormatter(formatter)
        audit_logger.addHandler(handler)
        
        return audit_logger

    def _setup_security_logger(self) -> logging.Logger:
        """Set up specialized security event logger.
        
        Returns:
            Configured security logger
        """
        if not self.enable_security_log:
            return logging.getLogger('security_disabled')
            
        security_logger = logging.getLogger('security')
        security_logger.setLevel(logging.INFO)
        security_logger.propagate = False
        
        handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "security" / "security.log",
            maxBytes=52428800,  # 50MB
            backupCount=10,
            encoding='utf-8'
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(event_id)s] - %(message)s'
        )
        handler.setFormatter(formatter)
        security_logger.addHandler(handler)
        
        return security_logger

    def _setup_integrations(self, config: Dict[str, Any]) -> None:
        """Set up optional logging integrations.
        
        Args:
            config: Logging configuration dictionary
        """
        # Sentry for error tracking
        if config.get('sentry_dsn'):
            import sentry_sdk
            sentry_sdk.init(
                dsn=config['sentry_dsn'],
                traces_sample_rate=config.get('sentry_trace_rate', 0.1)
            )
        
        # ELK Stack integration
        if config.get('elastic'):
            from cmreslogging.handlers import CMRESHandler
            handler = CMRESHandler(
                hosts=[config['elastic']['host']],
                auth_type=CMRESHandler.AuthType.API_KEY,
                api_key=config['elastic']['api_key'],
                index_name=f"{self.app_name}-logs"
            )
            logging.getLogger().addHandler(handler)

    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get a logger instance.
        
        Args:
            name: Optional logger name
            
        Returns:
            Configured logger instance
        """
        return logging.getLogger(name if name else self.app_name)

    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        security_related: bool = False
    ) -> None:
        """Log an error with optional context.
        
        Args:
            error: Exception to log
            context: Optional error context
            security_related: Whether this is a security-related error
        """
        logger = self.get_logger()
        event_id = str(uuid.uuid4())
        
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {},
            "event_id": event_id
        }
        
        logger.error(
            f"Error: {str(error)}",
            extra=error_data
        )
        
        if security_related:
            self.log_security_event(
                SecurityEventType.SECURITY_ALERT,
                error_data,
                severity="high"
            )

    async def log_audit_event(
        self,
        session_id: str,
        action: str,
        details: Dict[str, Any]
    ) -> str:
        """Log an audit event.
        
        Args:
            session_id: Session identifier
            action: Action being audited
            details: Event details
            
        Returns:
            Event ID
            
        Raises:
            LoggingError: If audit logging fails
        """
        try:
            if not self.enable_audit_log:
                return "audit_disabled"
                
            event_id = str(uuid.uuid4())
            event_data = {
                "event_id": event_id,
                "session_id": session_id,
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
                "details": details
            }
            
            # Calculate event hash for integrity
            event_hash = hashlib.sha256(
                json.dumps(event_data, sort_keys=True).encode()
            ).hexdigest()
            event_data["integrity_hash"] = event_hash
            
            self.audit_logger.info(
                f"Audit Event: {action}",
                extra=event_data
            )
            
            return event_id
            
        except Exception as e:
            raise LoggingError(f"Failed to log audit event: {str(e)}") from e

    def log_security_event(
        self,
        event_type: SecurityEventType,
        details: Dict[str, Any],
        severity: str = "medium"
    ) -> str:
        """Log a security event.
        
        Args:
            event_type: Type of security event
            details: Event details
            severity: Event severity
            
        Returns:
            Event ID
            
        Raises:
            LoggingError: If security logging fails
        """
        try:
            if not self.enable_security_log:
                return "security_disabled"
                
            event_id = str(uuid.uuid4())
            event_data = {
                "event_id": event_id,
                "event_type": event_type.value,
                "severity": severity,
                "timestamp": datetime.utcnow().isoformat(),
                "details": details
            }
            
            self.security_logger.warning(
                f"Security Event: {event_type.value}",
                extra=event_data
            )
            
            # Log critical events to main logger as well
            if severity in ["high", "critical"]:
                self.get_logger().critical(
                    f"Critical Security Event: {event_type.value}",
                    extra=event_data
                )
            
            return event_id
            
        except Exception as e:
            raise LoggingError(f"Failed to log security event: {str(e)}") from e

    async def export_audit_log(
        self,
        start_time: datetime,
        end_time: datetime,
        format: str = "json"
    ) -> Union[str, Dict[str, Any]]:
        """Export audit log entries within a time range.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            format: Output format ('json' or 'csv')
            
        Returns:
            Exported log data
            
        Raises:
            LoggingError: If export fails
        """
        try:
            # Implementation for audit log export
            pass
        except Exception as e:
            raise LoggingError(f"Failed to export audit log: {str(e)}") from e

    def rotate_logs(self) -> None:
        """Force rotation of all log files.
        
        Raises:
            LoggingError: If rotation fails
        """
        try:
            for handler in logging.getLogger().handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    handler.doRollover()
        except Exception as e:
            raise LoggingError(f"Failed to rotate logs: {str(e)}") from e
