"""
Logging configuration for EMODnet Viewer application
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10485760,
    backup_count: int = 5,
    enable_console: bool = True,
) -> logging.Logger:
    """
    Set up comprehensive logging for the application

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, only console logging)
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
        enable_console: Whether to enable console logging

    Returns:
        Configured logger instance
    """

    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logger = logging.getLogger("emodnet_viewer")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Add console handler if enabled
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if log_file is specified
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Set up specific loggers for different components
    _setup_component_loggers(log_level)

    return logger


def _setup_component_loggers(log_level: str):
    """Set up loggers for specific application components"""

    # WMS Service logger
    wms_logger = logging.getLogger("emodnet_viewer.wms")
    wms_logger.setLevel(getattr(logging, log_level.upper()))

    # API logger
    api_logger = logging.getLogger("emodnet_viewer.api")
    api_logger.setLevel(getattr(logging, log_level.upper()))

    # Flask logger
    flask_logger = logging.getLogger("emodnet_viewer.flask")
    flask_logger.setLevel(getattr(logging, log_level.upper()))

    # Requests logger (reduce verbosity)
    requests_logger = logging.getLogger("requests")
    requests_logger.setLevel(logging.WARNING)

    # urllib3 logger (reduce verbosity)
    urllib3_logger = logging.getLogger("urllib3")
    urllib3_logger.setLevel(logging.WARNING)


def get_logger(name: str = "emodnet_viewer") -> logging.Logger:
    """
    Get a logger instance for a specific component

    Args:
        name: Logger name (will be prefixed with 'emodnet_viewer.')

    Returns:
        Logger instance
    """
    if not name.startswith("emodnet_viewer"):
        name = f"emodnet_viewer.{name}"

    return logging.getLogger(name)


class LoggingMiddleware:
    """WSGI middleware for request/response logging"""

    def __init__(self, app, logger: Optional[logging.Logger] = None):
        self.app = app
        self.logger = logger or get_logger("middleware")

    def __call__(self, environ, start_response):
        """Log request and response information"""

        # Extract request information
        method = environ.get("REQUEST_METHOD", "UNKNOWN")
        path = environ.get("PATH_INFO", "/")
        query_string = environ.get("QUERY_STRING", "")
        remote_addr = environ.get("REMOTE_ADDR", "unknown")
        user_agent = environ.get("HTTP_USER_AGENT", "unknown")

        # Build request info
        request_info = f"{method} {path}"
        if query_string:
            request_info += f"?{query_string}"

        # Log request
        self.logger.info(f"Request: {request_info} from {remote_addr} - {user_agent}")

        # Capture response status
        def logging_start_response(status, headers, exc_info=None):
            self.logger.info(f"Response: {status} for {request_info}")
            return start_response(status, headers, exc_info)

        return self.app(environ, logging_start_response)


class PerformanceLogger:
    """Context manager for performance monitoring"""

    def __init__(self, operation_name: str, logger: Optional[logging.Logger] = None):
        self.operation_name = operation_name
        self.logger = logger or get_logger("performance")
        self.start_time = None

    def __enter__(self):
        import time

        self.start_time = time.time()
        self.logger.debug(f"Starting operation: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time

        duration = time.time() - self.start_time

        if exc_type is not None:
            self.logger.error(
                f"Operation '{self.operation_name}' failed after {duration:.3f}s: {exc_val}"
            )
        else:
            self.logger.info(f"Operation '{self.operation_name}' completed in {duration:.3f}s")


def log_wms_request(url: str, params: dict, logger: Optional[logging.Logger] = None):
    """Log WMS request details"""
    if logger is None:
        logger = get_logger("wms")

    logger.debug(f"WMS Request: {url}")
    logger.debug(f"WMS Parameters: {params}")


def log_wms_response(
    status_code: int, content_length: int, logger: Optional[logging.Logger] = None
):
    """Log WMS response details"""
    if logger is None:
        logger = get_logger("wms")

    logger.debug(f"WMS Response: {status_code} - {content_length} bytes")


def log_layer_discovery(layer_count: int, source: str, logger: Optional[logging.Logger] = None):
    """Log layer discovery results"""
    if logger is None:
        logger = get_logger("layers")

    logger.info(f"Discovered {layer_count} layers from {source}")


def log_application_startup(config_name: str, logger: Optional[logging.Logger] = None):
    """Log application startup information"""
    if logger is None:
        logger = get_logger("startup")

    logger.info(f"EMODnet Viewer starting with {config_name} configuration")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")


def log_error_with_context(
    error: Exception, context: dict, logger: Optional[logging.Logger] = None
):
    """Log error with additional context information"""
    if logger is None:
        logger = get_logger("error")

    error_msg = f"Error: {type(error).__name__}: {str(error)}"
    logger.error(error_msg)

    for key, value in context.items():
        logger.error(f"Context - {key}: {value}")

    # Log stack trace for debugging
    logger.debug("Stack trace:", exc_info=error)
