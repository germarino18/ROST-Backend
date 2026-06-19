import logging
import sys

def setup_logging(level_name: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)
    app_logger = logging.getLogger("app")
    app_logger.setLevel(getattr(logging, level_name))
    app_logger.handlers.clear()
    app_logger.addHandler(handler)
    app_logger.propagate = False
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
