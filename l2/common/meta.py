# dis разбирает код на составляющие: атрибуты и методы классов
import dis
from pprint import pprint


class ClientMeta(type):
    """
    Проверка корректности клиентов.
    """

    def __init__(cls, clsname, bases, clsdict):
        methods = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            # Если не функция - ловим исключение.
            except TypeError:
                pass
            # Иначе разбираем код, получая используемые методы.
            else:
                for el in ret:
                    if el.opname == 'LOAD_GLOBAL':
                        if el.argval not in methods:
                            methods.append(el.argval)

        # Методы 'accept', 'listen', 'socket' недопустимы.
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('Имеется запрещенный метод.')

        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')
        # Вызов конструктора предка.
        super().__init__(clsname, bases, clsdict)


class ServerMeta(type):
    def __init__(cls, clsname, bases, clsdict):
        """
        clsname - экземпляр метакласса - Server
        bases - кортеж базовых классов - ()
        clsdict - словарь атрибутов и методов экземпляра метакласса
        {'__module__': '__main__',
        '__qualname__': 'Server',
        'port': <descrptrs.Port object at 0x000000DACC8F5748>,
        '__init__': <function Server.__init__ at 0x000000DACCE3E378>,
        'init_socket': <function Server.init_socket at 0x000000DACCE3E400>,
        'main_loop': <function Server.main_loop at 0x000000DACCE3E488>,
        'process_message': <function Server.process_message at 0x000000DACCE3E510>,
        'process_client_message': <function Server.process_client_message at 0x000000DACCE3E598>}
        """
        methods_global = []
        methods = []
        attrs = []
        for func in clsdict:
            try:
                # Возвращает итератор по инструкциям в предоставленной функции исходного кода или в объекте кода.
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for el in ret:
                    # print(el)

                    if el.opname == 'LOAD_GLOBAL':
                        if el.argval not in methods_global:
                            # Методы, использующиеся в функциях класса.
                            methods_global.append(el.argval)
                    elif el.opname == 'LOAD_METHOD':
                        if el.argval not in methods:
                            # Методы, использующиеся в функциях класса.
                            methods.append(el.argval)
                    elif el.opname == 'LOAD_ATTR':
                        if el.argval not in attrs:
                            # Атрибуты, использующиеся в функциях класса.
                            attrs.append(el.argval)

        print(20 * '-', 'methods_global', 20 * '-')
        pprint(methods_global)
        print(20 * '-', 'methods', 20 * '-')
        pprint(methods)
        print(20 * '-', 'attrs', 20 * '-')
        pprint(attrs)
        print(50 * '-')

        # Метод 'connect' недопустим.
        if 'connect' in methods_global:
            raise TypeError('Использование метода connect недопустимо в серверном классе')

        # Инициализация сокета константами 'SOCK_STREAM'(TCP), 'AF_INET'(IPv4) обязательна.
        if not ('SOCK_STREAM' in methods_global and 'AF_INET' in methods_global):
            raise TypeError('Некорректная инициализация сокета.')

        super().__init__(clsname, bases, clsdict)
