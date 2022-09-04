import json
import sys
import time
import logging
import threading

from socket import socket, AF_INET, SOCK_STREAM
from PyQt5.QtCore import pyqtSignal, QObject

sys.path.append('../')
from common.errors import ServerError
from common.utils import get_message, send_message
from common.variables import (ACCOUNT_NAME, ACTION, ADD_CONTACT, DESTINATION, ERROR, EXIT, GET_CONTACTS, LIST_INFO,
                              MESSAGE, MESSAGE_TEXT, PRESENCE, REMOVE_CONTACT, RESPONSE, SENDER, TIME, USER,
                              USERS_REQUEST)

# Логгер и объект блокировки для работы с сокетом.
LOGGER = logging.getLogger('client')
socket_lock = threading.Lock()


class ClientTransport(threading.Thread, QObject):
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, ip, port, database, username):
        # Вызываем конструктор предка
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.database = database
        self.username = username
        self.transport = None
        self.connection_init(ip, port)

        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                LOGGER.critical('Lost connection to server')
                raise ServerError('Lost connection to server')
            LOGGER.error('Connection timeout when updating users lists')
        except json.JSONDecodeError:
            LOGGER.critical('Lost connection to server')
            raise ServerError('Lost connection to server')

        # Флаг продолжения работы транспорта.
        self.running = True

    # Функция инициализации соединения с сервером
    def connection_init(self, ip, port):
        # Инициализация сокета и сообщение серверу о нашем появлении
        self.transport = socket(AF_INET, SOCK_STREAM)
        # Таймаут необходим для освобождения сокета.
        self.transport.settimeout(5)
        # Соединяемся, 5 попыток соединения, флаг успеха ставим в True если удалось
        connected = False
        for i in range(5):
            LOGGER.info(f'Connection attempt #{i + 1}')
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)

        if not connected:
            LOGGER.critical('Failed to connect to server')
            raise ServerError('Failed to connect to server')

        LOGGER.debug('Successful connection to the server')

        # Посылаем серверу приветственное сообщение и получаем ответ,
        # что всё нормально или ловим исключение.
        try:
            with socket_lock:
                send_message(self.transport, self.create_presence())
                self.process_server_answer(get_message(self.transport))
        except (OSError, json.JSONDecodeError):
            LOGGER.critical('Lost connection to server')
            raise ServerError('Lost connection to server')

        LOGGER.info('Successful connection to the server')

    # Функция, генерирующая приветственное сообщение для сервера
    def create_presence(self):
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.username
            }
        }

        LOGGER.debug(f'Generated {PRESENCE} message for user {self.username}')
        return out

    # Функция, обрабатывающая сообщения от сервера. Ничего не возвращает.
    # Генерирует исключение при ошибке.
    def process_server_answer(self, message):
        LOGGER.debug(f'Parsing a message from the server: {message}')

        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(f'{message[ERROR]}')
            else:
                LOGGER.debug(f'Unknown verification code received: {message[RESPONSE]}')
        elif ACTION in message \
                and message[ACTION] == MESSAGE \
                and SENDER in message \
                and DESTINATION in message \
                and MESSAGE_TEXT in message \
                and message[DESTINATION] == self.username:
            LOGGER.debug(f'Message from user {message[SENDER]}: {message[MESSAGE_TEXT]}')
            self.database.save_message(message[SENDER], 'in', message[MESSAGE_TEXT])
            self.new_message.emit(message[SENDER])

    # Функция, обновляющая контакт - лист с сервера
    def contacts_list_update(self):
        LOGGER.debug(f'Request a contact list for user {self.name}')
        req = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.username,
        }
        LOGGER.debug(f'Request generated: {req}')
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        LOGGER.debug(f'Answer received {ans}')
        if RESPONSE in ans and ans[RESPONSE] == 202:
            for contact in ans[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            LOGGER.error('Failed to update contacts list')

    # Функция обновления таблицы известных пользователей.
    def user_list_update(self):
        LOGGER.debug(f'Query a list of known users {self.username}')
        req = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 202:
            self.database.add_users(ans[LIST_INFO])
        else:
            LOGGER.error('Failed to update list of known users.')

    # Функция сообщающая на сервер о добавлении нового контакта
    def add_contact(self, contact):
        LOGGER.debug(f'Create contact {contact}')
        req = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_server_answer(get_message(self.transport))

    # Функция удаления клиента на сервере
    def remove_contact(self, contact):
        LOGGER.debug(f'Deleting contact {contact}')
        req = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_server_answer(get_message(self.transport))

    # Функция закрытия соединения, отправляет сообщение о выходе.
    def transport_shutdown(self):
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            try:
                send_message(self.transport, message)
            except OSError:
                pass
        LOGGER.debug('Transport shuts down')
        time.sleep(0.5)

    # Функция отправки сообщения на сервер
    def send_message(self, to, message):
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.username,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        LOGGER.debug(f'Message dictionary generated: {message_dict}')

        # Необходимо дождаться освобождения сокета для отправки сообщения
        with socket_lock:
            send_message(self.transport, message_dict)
            self.process_server_answer(get_message(self.transport))
            LOGGER.info(f'Sent message to user {to}')

    def run(self):
        LOGGER.debug('The process is running - the receiver of messages from the server')
        while self.running:
            # Отдыхаем секунду и снова пробуем захватить сокет. Если не сделать тут задержку,
            # то отправка может достаточно долго ждать освобождения сокета.
            time.sleep(1)
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_message(self.transport)
                except OSError as err:
                    if err.errno:
                        # выход по таймауту вернёт номер ошибки err.errno равный None
                        # поэтому, при выходе по таймауту мы сюда попросту не попадём
                        LOGGER.critical(f'Lost connection to server')
                        self.running = False
                        self.connection_lost.emit()
                # Проблемы с соединением
                except (ConnectionError, ConnectionAbortedError,
                        ConnectionResetError, json.JSONDecodeError, TypeError):
                    LOGGER.debug(f'Lost connection to server')
                    self.running = False
                    self.connection_lost.emit()
                # Если сообщение получено, то вызываем функцию обработчик:
                else:
                    LOGGER.debug(f'Message received from the server: {message}')
                    self.process_server_answer(message)
                finally:
                    self.transport.settimeout(5)
