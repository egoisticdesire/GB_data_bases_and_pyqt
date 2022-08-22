import argparse
import configparser
import os.path
import select
import sys
import threading

from socket import AF_INET, SOCK_STREAM, socket, SOL_SOCKET, SO_REUSEADDR

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox

from db.server_db_config import ServerDB
from server_gui import ConfigWindow, create_stat_model, gui_create_model, HistoryWindow, MainWindow
from logs.server_log_config import LOGGER
from common.descriptor import Port
from common.meta import ServerMeta
from common.decorators import Log
from common.utils import get_message, send_message
from common.variables import ACCOUNT_NAME, ACTION, ADD_CONTACT, CONNECTION_TIMEOUT, DEFAULT_PORT, DESTINATION, ERROR, \
    EXIT, \
    GET_CONTACTS, LIST_INFO, MESSAGE, MESSAGE_TEXT, PRESENCE, REMOVE_CONTACT, RESPONSE_200, RESPONSE_202, RESPONSE_400, \
    SENDER, SERVER_CONFIG, TIME, \
    USER, USERS_REQUEST

# Флаг, что был подключён новый пользователь, нужен чтобы не мучить БД
# постоянными запросами на обновление
new_connection = False
conflag_lock = threading.Lock()


@Log
def args_parser(default_port, default_addr):
    """
    Парсим аргументы командной строки.
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=default_port, type=int, nargs='?')
    parser.add_argument('-a', default=default_addr, nargs='?')
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
                        for name in self.names:
                            if self.names[name] == client_with_msg:
                                self.database.user_logout(name)
                                del self.names[name]
                                break
                        self.clients.remove(client_with_msg)

            # Если есть сообщения - обрабатываем каждое.
            for msg in self.messages:
                try:
                    self.process_message(msg, send_list)
                except Exception as e:
                    LOGGER.info(f'Пользователь {msg[DESTINATION]} отключился.\n'
                                f'Причина: {e}')
                    self.clients.remove(self.names[msg[DESTINATION]])
                    self.database.user_logout(msg[DESTINATION])
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
        global new_connection
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
                client_ip, client_port = client.getpeername()
                self.database.user_login(
                        message[USER][ACCOUNT_NAME], client_ip, client_port)
                send_message(client, RESPONSE_200)
                with conflag_lock:
                    new_connection = True
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
            self.database.process_message(message[SENDER], message[DESTINATION])
            return
        # Если клиент выходит.
        elif ACTION in message \
                and message[ACTION] == EXIT \
                and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            self.database.user_logout(message[ACCOUNT_NAME])
            LOGGER.info(f'Пользователь {message[ACCOUNT_NAME]} корректно отключился от сервера.')
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            with conflag_lock:
                new_connection = True
            return
        # Если это запрос контакт-листа
        elif ACTION in message \
                and message[ACTION] == GET_CONTACTS \
                and USER in message \
                and self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_contacts(message[USER])
            send_message(client, response)
        # Если это добавление контакта
        elif ACTION in message \
                and message[ACTION] == ADD_CONTACT \
                and ACCOUNT_NAME in message \
                and USER in message \
                and self.names[message[USER]] == client:
            self.database.add_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client, RESPONSE_200)
        # Если это удаление контакта
        elif ACTION in message \
                and message[ACTION] == REMOVE_CONTACT \
                and ACCOUNT_NAME in message \
                and USER in message \
                and self.names[message[USER]] == client:
            self.database.remove_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client, RESPONSE_200)
        # Если это запрос известных пользователей
        elif ACTION in message \
                and message[ACTION] == USERS_REQUEST \
                and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = [user[0] for user in self.database.users_list()]
            send_message(client, response)
        # Иначе - Bad Request
        else:
            response = RESPONSE_400
            response[ERROR] = 'Некорректный запрос'
            send_message(client, response)
            return


def main():
    config = configparser.ConfigParser()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f'{dir_path}/server.ini')

    listen_addr, listen_port = args_parser(
            config['SETTINGS']['Default_port'],
            config['SETTINGS']['Listen_addr']
    )
    db = ServerDB(
            os.path.join(
                    config['SETTINGS']['Database_path'],
                    config['SETTINGS']['Database_file']
            )
    )

    # db.user_login('client_1', '192.168.1.4', 8888)
    # db.user_login('client_2', '192.168.1.5', 7777)

    server = Server(listen_addr, listen_port, db)
    server.daemon = True
    server.start()

    server_app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.statusBar().showMessage('Server working')
    main_window.active_clients_table.setModel(gui_create_model(db))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()

    def update_list():
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(gui_create_model(db))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    def show_statistics():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(db))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        stat_window.show()

    def server_config():
        global config_window

        config_window = ConfigWindow()
        config_window.db_path.insert(config['SETTINGS']['Database_path'])
        config_window.db_file.insert(config['SETTINGS']['Database_file'])
        config_window.port.insert(config['SETTINGS']['Default_port'])
        config_window.ip.insert(config['SETTINGS']['Listen_Addr'])
        config_window.save_btn.clicked.connect(save_server_config)

    def save_server_config():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['Database_path'] = config_window.db_path.text()
        config['SETTINGS']['Database_file'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            config['SETTINGS']['Listen_Addr'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['Default_port'] = str(port)
                print(port)
                with open('server.ini', 'w') as conf:
                    config.write(conf)
                    message.information(
                            config_window, 'OK', 'Настройки успешно сохранены!')
            else:
                message.warning(
                        config_window,
                        'Ошибка',
                        'Порт должен быть от 1024 до 65536')

    timer = QTimer()
    timer.timeout.connect(update_list)
    timer.start(1000)

    main_window.refresh_btn.triggered.connect(update_list)
    main_window.show_history_btn.triggered.connect(show_statistics)
    main_window.config_btn.triggered.connect(server_config)

    server_app.exec_()


if __name__ == '__main__':
    main()
