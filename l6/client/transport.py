import binascii
import hashlib
import hmac
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
from common.variables import (ACCOUNT_NAME, ACTION, ADD_CONTACT, CONNECTION_TIMEOUT, DATA, DESTINATION, ENCODING, ERROR,
                              EXIT, GET_CONTACTS,
                              LIST_INFO,
                              MESSAGE, MESSAGE_TEXT, PRESENCE, PUBLIC_KEY, PUBLIC_KEY_REQUEST, REMOVE_CONTACT, RESPONSE,
                              RESPONSE_511,
                              SENDER, TIME, USER,
                              USERS_REQUEST)

# Логгер и объект блокировки для работы с сокетом.
LOGGER = logging.getLogger('client')
socket_lock = threading.Lock()


class ClientTransport(threading.Thread, QObject):
    """
    Класс реализующий транспортную подсистему клиентского модуля. Отвечает за взаимодействие с сервером.
    """
    new_message = pyqtSignal(dict)
    message_205 = pyqtSignal()
    connection_lost = pyqtSignal()

    def __init__(self, port, ip, database, username, pswd, keys):
        # Вызываем конструктор предка
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.database = database
        self.username = username
        self.password = pswd
        self.keys = keys
        self.transport = None
        self.connection_init(port, ip)

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
    def connection_init(self, port, ip):
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

        LOGGER.debug('Starting auth dialog')

        # Запускаем процедуру авторизации
        # Получаем хэш пароля
        pswd_bytes = self.password.encode(ENCODING)
        salt = self.username.lower().encode(ENCODING)
        pswd_hash = hashlib.pbkdf2_hmac('sha512', pswd_bytes, salt, 10000)
        pswd_hash_str = binascii.hexlify(pswd_hash)

        LOGGER.debug(f'Passwd hash ready: {pswd_hash_str}')

        # Получаем публичный ключ и декодируем его из байтов
        public_key = self.keys.publickey().export_key().decode('ascii')

        # Авторизация на сервере
        with socket_lock:
            presence = {
                ACTION: PRESENCE,
                TIME: time.time(),
                USER: {
                    ACCOUNT_NAME: self.username,
                    PUBLIC_KEY: public_key
                }
            }
            LOGGER.debug(f'Presence message: {presence}')

            # Отправляем серверу приветственное сообщение
            try:
                send_message(self.transport, presence)
                answer = get_message(self.transport)
                LOGGER.debug(f'Server response: {answer}')

                # Если сервер вернул ошибку, бросаем исключение
                if RESPONSE in answer:
                    if answer[RESPONSE] == 400:
                        raise ServerError(answer[ERROR])

                    elif answer[RESPONSE] == 511:
                        # Если всё нормально, то продолжаем процедуру авторизации
                        answer_data = answer[DATA]
                        hash = hmac.new(pswd_hash_str, answer_data.encode(ENCODING), 'MD5')
                        digest = hash.digest()
                        my_answer = RESPONSE_511
                        my_answer[DATA] = binascii.b2a_base64(digest).decode('ascii')
                        send_message(self.transport, my_answer)
                        self.process_server_answer(get_message(self.transport))

            except (OSError, json.JSONDecodeError) as err:
                LOGGER.critical('Connection error.', exc_info=err)
                raise ServerError('Connection failure during authorization process')

    # Функция, обрабатывающая сообщения от сервера. Ничего не возвращает.
    # Генерирует исключение при ошибке.
    def process_server_answer(self, message):
        LOGGER.debug(f'Parsing a message from the server: {message}')

        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(f'{message[ERROR]}')
            elif message[RESPONSE] == 205:
                self.user_list_update()
                self.contacts_list_update()
                self.message_205.emit()
            else:
                LOGGER.debug(f'Unknown verification code received: {message[RESPONSE]}')

        elif ACTION in message \
                and message[ACTION] == MESSAGE \
                and SENDER in message \
                and DESTINATION in message \
                and MESSAGE_TEXT in message \
                and message[DESTINATION] == self.username:
            LOGGER.debug(f'Message from user {message[SENDER]}: {message[MESSAGE_TEXT]}')
            self.new_message.emit(message)

    # Функция, обновляющая контакт - лист с сервера
    def contacts_list_update(self):
        self.database.contacts_clear()
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

    def key_request(self, user):
        """Метод запрашивающий с сервера публичный ключ пользователя."""
        LOGGER.debug(f'Public key request for {user}')
        req = {
            ACTION: PUBLIC_KEY_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: user
        }
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 511:
            return ans[DATA]
        else:
            LOGGER.error(f'Failed to get key from {user}')

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
        time.sleep(CONNECTION_TIMEOUT)

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
            message = None

            with socket_lock:
                try:
                    self.transport.settimeout(CONNECTION_TIMEOUT)
                    message = get_message(self.transport)
                except OSError as err:
                    if err.errno:
                        # выход по таймауту вернёт номер ошибки err.errno равный None
                        # поэтому, при выходе по таймауту мы сюда попросту не попадём
                        LOGGER.critical(f'Lost connection to server')
                        self.running = False
                        self.connection_lost.emit()
                # Проблемы с соединением
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
                    LOGGER.debug(f'Lost connection to server')
                    self.running = False
                    self.connection_lost.emit()
                finally:
                    self.transport.settimeout(5)

            # Если сообщение получено, то вызываем функцию обработчик:
            if message:
                LOGGER.debug(f'Message received from the server: {message}')
                self.process_server_answer(message)
