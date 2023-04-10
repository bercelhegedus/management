import logging
import os

import logging
import os

def init_logger(log_file, level=logging.DEBUG):
    log_format = "%(asctime)s [%(levelname)s]: %(message)s"
    logging.basicConfig(filename=log_file, level=level, format=log_format, filemode="a")

    # Check if there's already a StreamHandler to prevent duplicates
    if not any(isinstance(handler, logging.StreamHandler) for handler in logging.getLogger().handlers):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(console_handler)

    return logging.getLogger()
