import logging
import os
from logging.handlers import RotatingFileHandler

from utils.load_config import config_loader as config

LOGS_DIR = config().logs_directory


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        file_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        stream_format = "%(levelname)s | %(message)s"

        file_handler = RotatingFileHandler(
            filename=os.path.join(LOGS_DIR, f"{name}.log"),
            mode="a",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(file_format))

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.WARNING)
        stream_handler.setFormatter(logging.Formatter(stream_format))

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
