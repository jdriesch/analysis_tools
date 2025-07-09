import logging

def setup(log_file=False, debug=False):
    # Configure basic logging settings

    if debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    handlers = [logging.StreamHandler()] # log to console

    if log_file:
        logfile = 'main.log'
        handlers.append(logging.FileHandler(logfile))  # log to file

    logging.basicConfig(
        level=log_level, 
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

    logger = logging.getLogger(__name__.split('.')[0]) # Get top-level logger
    return logger