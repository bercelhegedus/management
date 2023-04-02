import logging

def init_logger(file, level=logging.INFO):
    logger = logging.getLogger("app")
    logger.setLevel(level)
    
    log_formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')

    file_handler = logging.FileHandler(file, mode='a')
    file_handler.setFormatter(log_formatter)

    logger.addHandler(file_handler)

    return logger
