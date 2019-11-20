from os.path import dirname, realpath
from logging.handlers import BufferingHandler

from loguru import logger, _defaults

__path__ = dirname(realpath(__file__))

mem_handler = BufferingHandler(capacity=15000)
logger.add(mem_handler, colorize=_defaults.LOGURU_COLORIZE, level='INFO')
