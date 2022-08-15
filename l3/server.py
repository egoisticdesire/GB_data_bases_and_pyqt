import argparse
import select
import sys
import threading

from socket import AF_INET, SOCK_STREAM, socket, SOL_SOCKET, SO_REUSEADDR

from db.server_db_config import ServerDB
from logs.server_log_config import LOGGER
from common.descriptor import Port
from common.meta import ServerMeta
from common.decorators import Log
from common.utils import get_message, send_message
from common.variables import ACCOUNT_NAME, ACTION, CONNECTION_TIMEOUT, DEFAULT_PORT, DESTINATION, ERROR, EXIT, \
    MESSAGE, MESSAGE_TEXT, PRESENCE, RESPONSE_200, RESPONSE_400, SENDER, TIME, USER


@Log
def args_parser():
    """
    Парсим аргументы командной строки.
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_addr = namespace.a
    listen_port = namespace.p
    return listen_addr, listen_port


@Log
class Server(threading.Thread, metaclass=ServerMeta):
    port = Port()

    def __init__(self, listen_addr, listen_port, database):
        self.addr = listen_addr
        self.port = listen_port
        self.database = database

        self.sock = None
        self.clients = []
        self.messages = []
        self.names = {}
        super().__init__()

    def init_sock(self):
        LOGGER.info(f'Запущен сервер по адресу: {self.addr}:{self.port}. '
                    f'Если адрес не указан - принимаются соединения с любых адресов.')
        # with socket(AF_INET, SOCK_STREAM) as self.sock:
        #     self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        #     self.sock.bind((self.addr, self.port))
        #     self.sock.settimeout(CONNECTION_TIMEOUT)
        #     self.sock.listen(MAX_CONNECTIONS)
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind((self.addr, self.port))
        self.sock.settimeout(CONNECTION_TIMEOUT)
        self.sock.listen()

    def run(self):
        self.init_sock()

        while True:
            # Ждём подключения, если таймаут - ловим исключение
            try:
                client, client_addr = self.sock.accept()
            except OSError:
                pass
            else:
                LOGGER.info(f'Успешное соединение с {client_addr}')
                self.clients.append(client)

            recv_list = []
            send_list = []
            err_list = []

            # Проверяем на наличие ждущих клиентов
            try:
                if self.clients:
                    recv_list, send_list, err_list = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            # Принимаем сообщения и если ошибка - исключаем клиента.
            if recv_list:
                for client_with_msg in recv_list:
                    try:
                        self.process_client_message(get_message(client_with_msg), client_with_msg)
                    except:
                        LOGGER.info(f'Пользователь {client_with_msg.getpeername()} отключился от сервера.')
                        self.clients.remove(client_with_msg)

            # Если есть сообщения - обрабатываем каждое.
            for msg in self.messages:
                try:
                    self.process_message(msg, send_list)
                except Exception as e:
                    LOGGER.info(f'Пользователь {msg[DESTINATION]} отключился.\n'
                                f'Причина: {e}')
                    self.clients.remove(self.names[msg[DESTINATION]])
                    del self.names[msg[DESTINATION]]
            self.messages.clear()

    def process_message(self, message, listen_socks):
        """
        Адресная отправка сообщений конкретному клиенту.
        Принимает словарь сообщение, список зарегистрированных пользователей, слушающие сокеты.
        Ничего не возвращает.
        :param message:
        :param listen_socks:
        :return:
        """
        if message[DESTINATION] in self.names \
                and self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)
            LOGGER.info(f'Сообщение пользователю {message[DESTINATION]} от {message[SENDER]}.')
        elif message[DESTINATION] in self.names \
                and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            LOGGER.error(f'Пользователь {message[DESTINATION]} не зарегистрирован.')

    def process_client_message(self, message, client):
        """
        Принимает сообщение в виде словаря,
        проверяет корректность данных,
        возвращает ответ в виде словаря.
        :param message:
        :param client:
        :return:
        """
        LOGGER.debug(f'Разбор сообщения от клиента : {message}')
        # Если сообщение о присутствии - принимаем, отвечаем
        if ACTION in message \
                and message[ACTION] == PRESENCE \
                and TIME in message \
                and USER in message:
            # Регистрация имени пользователя
            # Иначе ответ с ошибкой
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Это имя уже используется.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        # Если обычное сообщение - добавляем в очередь. Ответ не требуется.
        elif ACTION in message \
                and message[ACTION] == MESSAGE \
                and DESTINATION in message \
                and TIME in message \
                and SENDER in message \
                and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        # Если клиент выходит.
        elif ACTION in message \
                and message[ACTION] == EXIT \
                and ACCOUNT_NAME in message:
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            return
            # Иначе - Bad Request
        else:
            response = RESPONSE_400
            response[ERROR] = 'Некорректный запрос'
            send_message(client, response)
            return


def print_help():
    print('Поддерживаемые команды:\n'
          'users, u - список известных пользователей\n'
          'connected, c - список подключённых пользователей\n'
          'hist, h - история входов пользователя\n'
          'exit, q - завершение работы сервера.\n'
          'help, ? - вывод справки по поддерживаемым командам')


def main():
    listen_addr, listen_port = args_parser()
    db = ServerDB()

    # db.user_login('client_1', '192.168.1.4', 8888)
    # db.user_login('client_2', '192.168.1.5', 7777)

    server = Server(listen_addr, listen_port, db)
    server.daemon = True
    server.start()

    print_help()

    while True:
        action = input('Введите команду: ')
        if action == 'help' or action == '?':
            print_help()
        elif action == 'exit' or action == 'q':
            break
        elif action == 'users' or action == 'u':
            for user in sorted(db.all_users_list()):
                print(f'Пользователь {user[0]}; последний вход: {user[1]}')
        elif action == 'connected' or action == 'c':
            for user in sorted(db.active_users_list()):
                print(f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
        elif action == 'hist' or action == 'h':
            name = input('Введите имя пользователя для просмотра истории. '
                         'Для вывода всей истории, просто нажмите Enter: ')
            for user in sorted(db.client_history_list(name)):
                print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
        else:
            print('Неизвестная команда.')


if __name__ == '__main__':
    main()
