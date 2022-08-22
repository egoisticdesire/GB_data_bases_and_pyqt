import argparse
import sys
import json
import threading

from time import sleep, time
from socket import AF_INET, SOCK_STREAM, socket

from db.client_db_config import ClientDB
from logs.client_log_config import LOGGER
from common.meta import ClientMeta
from common.decorators import Log
from common.utils import get_message, send_message
from common.variables import ACCOUNT_NAME, ACTION, ADD_CONTACT, DEFAULT_IP_ADDRESS, DEFAULT_PORT, DESTINATION, ERROR, \
    EXIT, \
    GET_CONTACTS, LIST_INFO, MESSAGE, \
    MESSAGE_TEXT, PRESENCE, REMOVE_CONTACT, RESPONSE, SENDER, TIME, USER, USERS_REQUEST

sock_lock = threading.Lock()
database_lock = threading.Lock()


@Log
class ClientSender(threading.Thread, metaclass=ClientMeta):
    def __init__(self, account_name, sock, db):
        self.account_name = account_name
        self.sock = sock
        self.db = db
        super().__init__()

    def create_exit_message(self):
        """
        Создание словаря с сообщением о выходе.
        :return:
        """
        return {
                ACTION: EXIT,
                TIME: time(),
                ACCOUNT_NAME: self.account_name
        }

    def create_message(self):
        """
        Запрашиваем имя получателя и текст сообщения.
        Отправляем на сервер.
        :return:
        """
        to_user = input('Имя получателя: ')
        message = input('Сообщение для отправки: ')

        # Проверим, что получатель существует
        with database_lock:
            if not self.db.check_user(to_user):
                LOGGER.error(f'Пользователя "{to_user}" не существует.')
                return

        message_dict = {
                ACTION: MESSAGE,
                SENDER: self.account_name,
                DESTINATION: to_user,
                TIME: time(),
                MESSAGE_TEXT: message
        }
        LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')

        with database_lock:
            self.db.save_message(self.account_name, to_user, message)

        with sock_lock:
            try:
                send_message(self.sock, message_dict)
                LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
            except OSError as err:
                if err.errno:
                    LOGGER.critical('Потеряно соединение с сервером.')
                    exit(1)
                else:
                    LOGGER.error('Не удалось передать сообщение. Таймаут соединения')

    def print_help(self):
        print('Поддерживаемые команды:\n '
              'help, ? - вывести подсказки по командам.\n '
              'message, m - отправить сообщение.\n '
              'contacts, c - отправить сообщение.\n '
              'edit, e - отправить сообщение.\n '
              'history, h - отправить сообщение.\n '
              'exit, q - выход из программы.\n')

    def run(self):
        """
        Взаимодействие с пользователем.
        :return:
        """
        self.print_help()
        while True:
            action = input('Выберите действие: ')
            if action == 'message' or action == 'm':
                self.create_message()
            elif action == 'help' or action == '?':
                self.print_help()
            elif action == 'exit' or action == 'q':
                with sock_lock:
                    try:
                        send_message(self.sock, self.create_exit_message())
                    except:
                        pass
                    print('Соединение разорвано.')
                    LOGGER.info('Завершение работы по команде пользователя.')
                sleep(0.5)
                break
            elif action == 'contacts' or action == 'c':
                with database_lock:
                    contacts_list = self.db.get_contacts()
                for contact in contacts_list:
                    print(contact)
            elif action == 'edit' or action == 'e':
                self.edit_contacts()
            elif action == 'history' or action == 'h':
                self.print_history()
            else:
                print('Неизвестная команда.\n '
                      'help, ? - вывести поддерживаемые команды.\n')

    def print_history(self):
        ask = input('Показать сообщения:\n'
                    'in - входящие\n'
                    'out - исходящие\n'
                    'Нажать Enter для отображения всех сообщений\n'
                    ': ')
        with database_lock:
            if ask == 'in':
                history_list = self.db.get_hisrtory(to_who=self.account_name)
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]} '
                          f'от {message[3]}:\n{message[2]}')
            elif ask == 'out':
                history_list = self.db.get_history(from_who=self.account_name)
                for message in history_list:
                    print(f'\nСообщение пользователю: {message[1]} '
                          f'от {message[3]}:\n{message[2]}')
            else:
                history_list = self.db.get_history()
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]},'
                          f' пользователю {message[1]} '
                          f'от {message[3]}\n{message[2]}')

    def edit_contacts(self):
        ans = input('Введите:\n'
                    'del - для удаления\n'
                    'add - для добавления\n'
                    ': ')
        if ans == 'del':
            edit = input('Введите имя удаляемого контакта: ')
            with database_lock:
                if self.db.check_contact(edit):
                    self.db.del_contact(edit)
                else:
                    LOGGER.error('Попытка удаления несуществующего контакта.')
        elif ans == 'add':
            # Проверка на возможность такого контакта
            edit = input('Введите имя создаваемого контакта: ')
            if self.db.check_user(edit):
                with database_lock:
                    self.db.add_contact(edit)
                with sock_lock:
                    add_contact(self.sock, self.account_name, edit)


@Log
class ClientReceiver(threading.Thread, metaclass=ClientMeta):
    def __init__(self, account_name, sock, db):
        self.account_name = account_name
        self.sock = sock
        self.db = db
        super().__init__()

    def run(self):
        """
        Обрабатываем сообщения других пользователей.
        :return:
        """

        while True:
            sleep(1)
            with sock_lock:
                try:
                    message = get_message(self.sock)

                except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                    LOGGER.critical('Потеряно соединение с сервером.')
                    break
                else:
                    if ACTION in message and message[ACTION] == MESSAGE \
                            and SENDER in message \
                            and DESTINATION in message \
                            and MESSAGE_TEXT in message \
                            and message[DESTINATION] == self.account_name:
                        print(f'\n Получено сообщение от пользователя '
                              f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                        # Захватываем работу с базой данных и сохраняем в неё сообщение
                        with database_lock:
                            try:
                                self.db.save_message(
                                        message[SENDER],
                                        self.account_name,
                                        message[MESSAGE_TEXT]
                                )
                            except Exception as e:
                                print(e)
                                LOGGER.error('Ошибка взаимодействия с базой данных')

                        LOGGER.info(f'Получено сообщение от пользователя '
                                    f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    else:
                        LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')


@Log
def create_presence(account_name):
    """
    Генерируем запрос на присутствие клиента.
    :param account_name:
    :return:
    """
    out_msg = {
            ACTION: PRESENCE,
            TIME: time(),
            USER: {
                    ACCOUNT_NAME: account_name
            }
    }
    LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out_msg


@Log
def process_server_message(message):
    """
    Принимает сообщение в виде словаря,
    проверяет корректность данных,
    возвращает ответ в виде словаря.
    :param message:
    :return:
    """
    LOGGER.debug(f'Разбор приветственного сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        elif message[RESPONSE] == 400:
            return f'400: {message[ERROR]}'
    raise ValueError


@Log
def args_parser():
    """
    Парсим аргументы командной строки.
    Читаем параметры, возвращаем 3 параметра.
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_addr = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # Проверяем порт
    if not 1023 < server_port < 65536:
        LOGGER.error(f'Порт {server_port} недопустим. Возможны варианты от 1024 до 65535.')
        exit(1)

    return server_addr, server_port, client_name


def contacts_list_request(sock, name):
    LOGGER.debug(f'Запрос контакт листа для пользователя {name}')
    req = {
            ACTION: GET_CONTACTS,
            TIME: time(),
            USER: name
    }
    LOGGER.debug(f'Сформирован запрос {req}')
    send_message(sock, req)
    ans = get_message(sock)
    LOGGER.debug(f'Получен ответ {ans}')
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]


# Функция добавления пользователя в контакт лист
def add_contact(sock, username, contact):
    LOGGER.debug(f'Создание контакта {contact}')
    req = {
            ACTION: ADD_CONTACT,
            TIME: time(),
            USER: username,
            ACCOUNT_NAME: contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    print('Удачное создание контакта.')


# Функция запроса списка известных пользователей
def user_list_request(sock, username):
    LOGGER.debug(f'Запрос списка известных пользователей {username}')
    req = {
            ACTION: USERS_REQUEST,
            TIME: time(),
            ACCOUNT_NAME: username
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]


# Функция удаления пользователя из списка контактов
def remove_contact(sock, username, contact):
    LOGGER.debug(f'Удаление контакта {contact}')
    req = {
            ACTION: REMOVE_CONTACT,
            TIME: time(),
            USER: username,
            ACCOUNT_NAME: contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    print('Удачное удаление контакта')


# Функция инициализатор базы данных.
# Запускается при запуске, загружает данные в базу с сервера.
def database_load(sock, database, username):
    # Загружаем список известных пользователей
    try:
        users_list = user_list_request(sock, username)
    except:
        LOGGER.error('Ошибка запроса списка известных пользователей.')
    else:
        database.add_users(users_list)

    # Загружаем список контактов
    try:
        contacts_list = contacts_list_request(sock, username)
    except:
        LOGGER.error('Ошибка запроса списка контактов.')
    else:
        for contact in contacts_list:
            database.add_contact(contact)


def main():
    print('Консольный мессенджер. Клиентский модуль.')

    server_addr, server_port, client_name = args_parser()

    if not client_name:
        client_name = input('Имя пользователя: ')
    else:
        print(f'Вы вошли под именем {client_name}.')

    LOGGER.info(f'Клиент запущен с параметрами: {server_addr}:{server_port}; имя пользователя: {client_name}')

    try:
        transport = socket(AF_INET, SOCK_STREAM)

        # Таймаут 1 секунда, необходим для освобождения сокета.
        transport.settimeout(1)

        transport.connect((server_addr, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_server_message(get_message(transport))
        LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        LOGGER.error('Сообщение сервера не декодировано.')
        exit(1)
    except TypeError:
        LOGGER.error('Попытка отправки некорректного сообщения на сервер.')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        LOGGER.error(f'Не удалось подключиться к серверу {server_addr}:{server_port}')
        exit(1)
    else:
        # Инициализация БД
        database = ClientDB(client_name)
        database_load(transport, database, client_name)

        # Если соединение с сервером установлено корректно:
        # запускаем отправку сообщений и взаимодействие с пользователем.
        sender = ClientSender(client_name, transport, database)
        sender.daemon = True
        sender.start()

        # запускаем клиентский процесс приёма сообщений.
        receiver = ClientReceiver(client_name, transport, database)
        receiver.daemon = True
        receiver.start()

        LOGGER.debug('Процессы запущены.')

        # проверяем потоки на предмет соединения.
        while True:
            sleep(1)
            if receiver.is_alive() and sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
