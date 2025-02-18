import logging


def setup_logger(name) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        info_handler = logging.StreamHandler()
        info_formatter = logging.Formatter("%(levelname)s | %(asctime)s | %(message)s")
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(info_formatter)
        trace_handler = logging.StreamHandler()
        trace_formatter = logging.Formatter(
            "%(levelname)s | %(asctime)s | %(filename)s | %(lineno)d > %(message)s"
        )
        trace_handler.setLevel(logging.ERROR)
        trace_handler.setFormatter(trace_formatter)
        logger.addHandler(info_handler)
        logger.addHandler(trace_handler)
    return logger
