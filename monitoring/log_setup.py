import logging


def log_setup():
    logger = logging.getLogger('monitoring')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('monitoring.log')
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return(logger)
