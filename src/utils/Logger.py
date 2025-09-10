import logging
import os
import sys

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
numeric_level = getattr(logging, LOG_LEVEL, None)
if not isinstance(numeric_level, int):
    raise ValueError(f"Invalid log level: {LOG_LEVEL}")

logger = logging.getLogger("FranchiseGPT_app_logger")
logger.setLevel(numeric_level)

logger.propagate = False

if not logger.handlers:
    stream_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter('{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    print(f"Application logging initialized to console (stdout) with level: {LOG_LEVEL}")

