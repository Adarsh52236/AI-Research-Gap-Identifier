import logging
import sys
from backend.app.config import settings

def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(settings.LOG_LEVEL)
        handler = logging.StreamHandler(sys.stdout)
        
        # Format that supports request_id via log record (injected by middleware if present)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [req_id: %(request_id)s] - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Add a default filter to always provide a request_id if not present
        class RequestIdFilter(logging.Filter):
            def filter(self, record):
                if not hasattr(record, 'request_id'):
                    record.request_id = 'N/A'
                return True
                
        logger.addFilter(RequestIdFilter())
        
    return logger
