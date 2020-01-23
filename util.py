import sys
import logging
import coloredlogs


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)

    logger.addHandler(stdout_handler)

    coloredlogs.install(logger=logger)

    return logger