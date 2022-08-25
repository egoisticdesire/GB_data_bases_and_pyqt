import logging.handlers
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), '..'))
from common.variables import ENCODING, LOGGING_LVL, DEFAULT_LOG_NAME

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{DEFAULT_LOG_NAME}.log')

LOGGER = logging.getLogger(DEFAULT_LOG_NAME)
FORMATTER = logging.Formatter(
        '{asctime} :: {levelname:8s} :: {name} :: {message}',
        style='{',
        datefmt='%Y-%m-%d %H:%M:%S'
)

FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(PATH, encoding=ENCODING, when='D')
FILE_HANDLER.setFormatter(FORMATTER)

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)

LOGGER.addHandler(FILE_HANDLER)
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.setLevel(LOGGING_LVL)

if __name__ == '__main__':
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')
    LOGGER.warning('Предупреждение')
    LOGGER.error('Ошибка')
    LOGGER.critical('Критическая ошибка')
