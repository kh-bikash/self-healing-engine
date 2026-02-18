import logging
import sys
import json
from typing import Any

class StructuredLogger(logging.Logger):
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
        if extra is None:
            extra = {}
        
        # Add standardized fields
        log_entry = {
            "level": logging.getLevelName(level),
            "message": msg,
            **extra
        }
        
        # If there's an exception, add it
        if exc_info:
            log_entry["exception"] = self._format_exception(exc_info)

        # Use json.dumps for structured output
        # In a real heavy-load scenario, we might use orjson
        super()._log(level, json.dumps(log_entry), args, exc_info=None, extra=None, stack_info=stack_info, stacklevel=stacklevel)

    def _format_exception(self, exc_info):
        return str(exc_info[1]) if exc_info else None

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Check if handler already exists
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)
    
    return logger
