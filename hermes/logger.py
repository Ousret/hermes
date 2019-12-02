from os.path import dirname, realpath
from logging.handlers import BufferingHandler

from loguru import logger

__path__ = dirname(realpath(__file__))

mem_handler = BufferingHandler(capacity=15000)
logger.add(mem_handler, colorize=False, level='INFO', enqueue=False)
