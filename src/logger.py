import logging
import datetime
import os


if not os.path.exists('logs'):
    os.makedirs('logs')

FILENAME = f'logs/{datetime.date.today()}.log'
FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

logger = logging.getLogger(name="electrobot")
logger.setLevel(logging.DEBUG)

# Create handlers
c_handler = logging.StreamHandler(stream=None)
f_handler = logging.FileHandler(FILENAME)
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt=DATE_FORMAT)
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)