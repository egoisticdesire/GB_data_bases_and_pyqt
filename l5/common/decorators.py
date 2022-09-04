import os
import sys
import functools
import inspect
import logging

sys.path.insert(0, os.path.join(os.getcwd(), '..'))
from common.variables import DEFAULT_LOG_NAME


class Log:
    def __init__(self, func):
        # functools.update_wrapper(self, func)
        self.func = func

    def __call__(self, *args, **kwargs):
        # Определяем, откуда была вызвана функция (получение имени метода)
        code_object_name = inspect.currentframe().f_back.f_code.co_name

        logger = logging.getLogger(DEFAULT_LOG_NAME)
        _args = args if args else ''
        _kwargs = kwargs if kwargs else ''
        logger.info(
                f'Из "{code_object_name}()" вызвана функция "{self.func.__name__}()" с параметрами:\n\t{_args}{_kwargs}')

        return self.func(*args, **kwargs)
