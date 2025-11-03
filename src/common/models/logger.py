import logging
import os
import inspect
import datetime
import json
from typing import Dict, Any, Optional


class Logger:
    """Simple and robust logging utility with JSON output and metadata."""

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, loggername: str = "app_logger"):
        """Initializes the logger."""
        if self._initialized:
            return

        self._metadata: Dict[str, Any] = {}
        self._tempdata: Dict[str, Any] = {}

        # Configure root logger
        root_logger = logging.getLogger()
        if root_logger.handlers:
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
        
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(message)s",
            force=True
        )

        self.logger = logging.getLogger(loggername)
        self.logger.setLevel(logging.INFO)
        self._initialized = True

    def _log(self, level: int, msg: str) -> None:
        """Internal logging method."""
        if not self.logger.isEnabledFor(level):
            return

        try:
            # Get caller info
            frame = inspect.currentframe()
            caller_frame = frame.f_back.f_back if frame and frame.f_back else None
            
            if caller_frame:
                info = inspect.getframeinfo(caller_frame)
                function = info.function
                filename = os.path.basename(info.filename)
                line = info.lineno
            else:
                function = "unknown"
                filename = "unknown"
                line = 0

            # Build log entry
            log_entry = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "level": logging.getLevelName(level),
                "message": str(msg),
                "function": function,
                "file": filename,
                "line": line,
            }

            # Add metadata if exists
            if self._metadata:
                log_entry.update(self._metadata)
            
            # Add tempdata if exists
            if self._tempdata:
                log_entry.update(self._tempdata)

            # Log the entry
            self.logger.log(level, json.dumps(log_entry, ensure_ascii=False, default=str))

        except Exception as e:
            fallback = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "level": "ERROR",
                "message": f"Logging failed: {e}. Original: {msg}"
            }
            self.logger.error(json.dumps(fallback, default=str))
        finally:
            self._tempdata.clear()

    def debug(self, msg: str) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, msg)

    def info(self, msg: str) -> None:
        """Log info message."""
        self._log(logging.INFO, msg)

    def warning(self, msg: str) -> None:
        """Log warning message."""
        self._log(logging.WARNING, msg)

    def error(self, msg: str) -> None:
        """Log error message."""
        self._log(logging.ERROR, msg)

    def critical(self, msg: str) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, msg)

    def set_metadata(self, key_values: Optional[Dict[str, Any]]) -> None:
        """Sets persistent metadata for all logs."""
        self._metadata = key_values.copy() if key_values else {}

    def add_metadata(self, key: str, value: Any) -> None:
        """Adds a key-value pair to persistent metadata."""
        if key is not None:
            self._metadata[key] = value

    def add_tempdata(self, key: str, value: Any) -> None:
        """Adds temporary data for the next log only."""
        if key is not None:
            self._tempdata[key] = value
        self._log(logging.ERROR, f"context_message: {key}={value}")

    def init_context(self, context: Optional[Any] = None) -> None:
        """
        Initializes logging context with information from the AWS Lambda environment.

        This method should be called at the beginning of your Lambda handler.
        It extracts the AWS Request ID from the Lambda context object and other
        details (like function name, version, and region) from environment variables.

        Args:
            context: The context object provided to the Lambda handler.
        """
        context_data = {}

        # Extract info from the Lambda context object, if provided
        if context and hasattr(context, "aws_request_id"):
            context_data["aws_request_id"] = context.aws_request_id

        # Extract info from Lambda environment variables
        for key, env_var in [
            ("function_name", "AWS_LAMBDA_FUNCTION_NAME"),
            ("region", "AWS_REGION"),
            ("version", "AWS_LAMBDA_FUNCTION_VERSION"),
        ]:
            value = os.environ.get(env_var)
            if value:
                context_data[key] = value

        self.set_metadata(context_data)