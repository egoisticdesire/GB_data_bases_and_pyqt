import os
import sys
import inspect
import logging
from socket import socket

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
            f'Из "{code_object_name}()" вызвана функция "{self.func.__name__}()" с параметрами:\n\t{_args}{_kwargs}. '
        )

        return self.func(*args, **kwargs)


# class LoginRequired:
#     def __init__(self, func):
#         self.func = func
#
#     def __call__(self, *args, **kwargs):
#         from server.core import MessageProcessor
#         from common.variables import ACTION, PRESENCE
#
#         if isinstance(args[0], MessageProcessor):
#             found = False
#
#             for arg in args:
#                 if isinstance(arg, socket):
#                     # Проверяем, что данный сокет есть в списке names класса
#                     # MessageProcessor
#                     for client in args[0].names:
#                         if args[0].names[client] == arg:
#                             found = True
#
#             # Проверяем, что передаваемые аргументы не presence сообщение
#             # Если presence, то разрешаем
#             for arg in args:
#                 if isinstance(arg, dict):
#                     if ACTION in arg and arg[ACTION] == PRESENCE:
#                         found = True
#
#             # Если не авторизован и не сообщение начала авторизации, то вызываем исключение
#             if not found:
#                 raise TypeError
#
#         return self.func(*args, **kwargs)


def login_required(func):
    """
    Декоратор, проверяющий, что клиент авторизован на сервере.
    Проверяет, что передаваемый объект сокета находится в
    списке авторизованных клиентов.
    За исключением передачи словаря-запроса
    на авторизацию. Если клиент не авторизован,
    генерирует исключение TypeError
    """

    def checker(*args, **kwargs):
        # проверяем, что первый аргумент - экземпляр MessageProcessor
        # Импортить необходимо тут, иначе ошибка рекурсивного импорта.
        # ----------------------------------------------------------------
        # args = (
        #         <MessageProcessor(Thread-5, started daemon 140650633856768)>,
        #         {'action': 'presence',
        #          'time': 1654900198.8001323,
        #           'user': {
        #                    'account_name': 'test1',
        #                    'pubkey': '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAmKN/CFSxgU8eu0oO0oKw\n29WTZQSfqw/mJgEtr8nLUAOHGcg3kT7epUgPfwbo/V67sJlGhb/UD7dPK81utWRn\nFKhhUGuo+ad/4HnvbSQjIHy2Wbr85T4gJCL1IqTkodAgSOo4Nuv/Qq9r5po0dNIC\nF4YTZrzfCy6V0v349iXM2CXf+/14fHCxsm3OkNCUwHsOW6nzh5fIyAs1UhssJm/Z\nbCNzX5PkRjI7bwBJhoXHNgS1fDyII6vGrQAyAwxU0hKrBAtAzYIon5ZlIYxyF2/5\nKb8IVmLmnrvCpmtjTQ4u80Dp6YuErMCD82GzgUi50UdQoW617AmFxaKpvO7Lu+aA\nfwIDAQAB\n-----END PUBLIC KEY-----'
        #                    }
        #          },
        #          <socket.socket fd=25, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 7777), raddr=('127.0.0.1', 52416)>
        # )
        from server.core import MessageProcessor
        from common.variables import ACTION, PRESENCE

        if isinstance(args[0], MessageProcessor):
            found = False
            for arg in args:
                if isinstance(arg, socket):
                    # Проверяем, что данный сокет есть в списке names класса
                    # MessageProcessor
                    for client in args[0].names:
                        # args[0].names = {'test1': <socket.socket fd=25, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 7777), raddr=('127.0.0.1', 52420)>}
                        if args[0].names[client] == arg:
                            found = True

            # Теперь надо проверить, что передаваемые аргументы не presence
            # сообщение. Если presence, то разрешаем
            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            # Если не не авторизован и не сообщение начала авторизации, то
            # вызываем исключение.
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker
