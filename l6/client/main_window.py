import base64
import json
import sys
import logging

from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox, QApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtCore import pyqtSlot, Qt

from common.variables import ENCODING, MESSAGE_TEXT, SENDER

sys.path.append('../')
from common.qss import style
from client.main_window_config import Ui_MainClientWindow
from client.add_contact import AddContactDialog
from client.del_contact import DelContactDialog
from common.errors import ServerError

LOGGER = logging.getLogger('client')


class ClientMainWindow(QMainWindow):
    def __init__(self, database, transport, keys):
        super().__init__()
        self.database = database
        self.transport = transport
        # Дешифровщик сообщений с предзагруженным ключом
        self.decrypter = PKCS1_OAEP.new(keys)

        # Загружаем конфигурацию окна из дизайнера
        self.ui = Ui_MainClientWindow()
        self.ui.setupUi(self)

        # Кнопка "Выход"
        self.ui.menu_exit.triggered.connect(qApp.exit)

        # Кнопка "Отправить сообщение"
        self.ui.send_btn.clicked.connect(self.send_message)

        # Кнопка "Добавить контакт"
        self.ui.add_contact_btn.clicked.connect(self.add_contact_window)
        self.ui.menu_add_contact.triggered.connect(self.add_contact_window)

        # Кнопка "Удалить контакт"
        self.ui.remove_contact_btn.clicked.connect(self.delete_contact_window)
        self.ui.menu_del_contact.triggered.connect(self.delete_contact_window)

        # Дополнительные требующиеся атрибуты
        self.contacts_model = None
        self.history_model = None
        self.current_chat = None
        self.current_chat_key = None
        self.encryptor = None
        self.messages = QMessageBox()
        self.messages.setStyleSheet(style.COMMON_THEME)
        self.ui.messages_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.messages_list.setWordWrap(True)

        # Даблклик по листу контактов отправляется в обработчик
        self.ui.contacts_list.clicked.connect(self.select_active_user)

        self.clients_list_update()
        self.set_disabled_input()
        self.show()

    # Деактивация поля ввода
    def set_disabled_input(self):
        self.ui.new_message_label.setText('Select a chat to start messaging')

        self.ui.message_text.clear()
        if self.history_model:
            self.history_model.clear()

        # Поле ввода и кнопка отправки неактивны до выбора получателя
        self.ui.clear_btn.setDisabled(True)
        self.ui.clear_btn.setVisible(False)
        self.ui.send_btn.setDisabled(True)
        self.ui.send_btn.setVisible(False)
        self.ui.message_text.setDisabled(True)
        self.ui.message_text.setVisible(False)
        self.ui.new_message_label.setVisible(True)

        self.encryptor = None
        self.current_chat = None
        self.current_chat_key = None

    # Заполняем историю сообщений.
    def history_list_update(self):
        messages_list = sorted(
            self.database.get_history(self.current_chat),
            key=lambda item: item[3]
        )

        # Создаем модель, если не создана
        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.ui.messages_list.setModel(self.history_model)

        # Очистим от старых записей
        self.history_model.clear()

        # Берём не более 20 последних записей.
        length = len(messages_list)
        start_idx = 0
        if length > 20:
            start_idx = length - 20

        # Заполнение модели записями, так же стоит разделить входящие и исходящие
        # сообщения выравниванием и разным фоном.
        # Записи в обратном порядке, поэтому выбираем их с конца и не более 20
        for i in range(start_idx, length):
            item = messages_list[i]

            if item[1] == 'in':
                msg = QStandardItem(f'{self.current_chat}:\n{item[2]}\n{item[3].replace(microsecond=0)}')
                msg.setEditable(False)
                msg.setBackground(QBrush(QColor(255, 213, 213)))
                msg.setForeground(QBrush(QColor(27, 31, 37)))
                msg.setTextAlignment(Qt.AlignLeft)
                self.history_model.appendRow(msg)
            else:
                msg = QStandardItem(f'{item[2]}\n{item[3].replace(microsecond=0)}')
                msg.setEditable(False)
                msg.setTextAlignment(Qt.AlignRight)
                msg.setBackground(QBrush(QColor(204, 255, 204)))
                msg.setForeground(QBrush(QColor(27, 31, 37)))
                self.history_model.appendRow(msg)
        self.ui.messages_list.scrollToBottom()

    # Функция обработчик double click по контакту
    def select_active_user(self):
        # Выбранный пользователем контакт находится в выделенном элементе в QListView
        self.current_chat = self.ui.contacts_list.currentIndex().data()

        # вызываем основную функцию
        self.set_active_user()

    # Функция, устанавливающая активного собеседника
    def set_active_user(self):
        self.setStyleSheet(style.COMMON_THEME)
        # Запрашиваем публичный ключ пользователя и создаём объект шифрования
        try:
            self.current_chat_key = self.transport.key_request(self.current_chat)
            LOGGER.debug(f'Uploaded public key for {self.current_chat}')
            if self.current_chat_key:
                self.encryptor = PKCS1_OAEP.new(RSA.import_key(self.current_chat_key))
        except (OSError, json.JSONDecodeError):
            self.current_chat_key = None
            self.encryptor = None
            LOGGER.debug(f'Failed to get key for {self.current_chat}')

        if not self.current_chat_key:
            self.messages.warning(self, 'Error', 'The selected user does not have an encryption key')
            return

        # Активируем кнопки
        self.ui.clear_btn.setDisabled(False)
        self.ui.clear_btn.setVisible(True)
        self.ui.send_btn.setDisabled(False)
        self.ui.send_btn.setVisible(True)
        self.ui.message_text.setDisabled(False)
        self.ui.message_text.setVisible(True)
        self.ui.new_message_label.setVisible(False)

        # Заполняем историю сообщений по требуемому пользователю.
        self.history_list_update()

    # Функция, обновляющая контакт-лист
    def clients_list_update(self):
        contacts_list = self.database.get_contacts()
        self.contacts_model = QStandardItemModel()

        for i in sorted(contacts_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.ui.contacts_list.setModel(self.contacts_model)

    # Функция добавления контакта
    def add_contact_window(self):
        global select_dialog
        select_dialog = AddContactDialog(self.transport, self.database)
        select_dialog.add_btn.clicked.connect(lambda: self.add_contact_action(select_dialog))

        select_dialog.show()

    # Функция - обработчик добавления, сообщает серверу, обновляет таблицу и список контактов
    def add_contact_action(self, item):
        new_contact = item.selector.currentText()
        self.add_contact(new_contact)
        item.close()

    # Функция, добавляющая контакт в БД
    def add_contact(self, new_contact):
        self.setStyleSheet(style.COMMON_THEME)
        try:
            self.transport.add_contact(new_contact)
        except ServerError as err:
            self.messages.critical(self, 'Server error', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Error', 'Lost connection to server')
                self.close()
            self.messages.critical(self, 'Error', 'Connection timeout')
        else:
            self.database.add_contact(new_contact)
            new_contact = QStandardItem(new_contact)
            new_contact.setEditable(False)
            self.contacts_model.appendRow(new_contact)
            LOGGER.info(f'Successfully added contact: {new_contact}')
            self.messages.information(self, 'Success', 'Contact successfully added')

    # Функция удаления контакта
    def delete_contact_window(self):
        global remove_dialog
        self.setStyleSheet(style.COMMON_THEME)
        remove_dialog = DelContactDialog(self.database)
        remove_dialog.del_btn.clicked.connect(lambda: self.delete_contact(remove_dialog))

        remove_dialog.show()

    # Функция-обработчик удаления контакта: сообщает на сервер, обновляет таблицу контактов
    def delete_contact(self, item):
        self.setStyleSheet(style.COMMON_THEME)
        selected = item.selector.currentText()
        try:
            self.transport.remove_contact(selected)
        except ServerError as err:
            self.messages.critical(self, 'Server error', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Error', 'Lost connection to server')
                self.close()
            self.messages.critical(self, 'Error', 'Connection timeout')
        else:
            self.database.del_contact(selected)
            self.clients_list_update()
            LOGGER.info(f'Successfully deleted contact {selected}')
            self.messages.information(self, 'Success', 'Contact successfully deleted')
            item.close()
            # Если удалён активный пользователь, то деактивируем поля ввода.
            if selected == self.current_chat:
                self.current_chat = None
                self.set_disabled_input()

    # Функция отправки сообщения пользователю.
    def send_message(self):
        self.setStyleSheet(style.COMMON_THEME)
        # Текст в поле, проверяем что поле не пустое затем забирается сообщение и поле очищается
        message_text = self.ui.message_text.toPlainText()
        self.ui.message_text.clear()
        if not message_text:
            return

        # Шифруем сообщение ключом получателя и упаковываем в base64.
        message_text_encrypted = self.encryptor.encrypt(message_text.encode(ENCODING))
        message_text_encrypted_base64 = base64.b64encode(message_text_encrypted)

        try:
            self.transport.send_message(self.current_chat, message_text_encrypted_base64.decode('ascii'))
            pass
        except ServerError as err:
            self.messages.critical(self, 'Error', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Error', 'Lost connection to server')
                self.close()
            self.messages.critical(self, 'Error', 'Connection timeout')
        except (ConnectionResetError, ConnectionAbortedError):
            self.messages.critical(self, 'Error', 'Lost connection to server')
            self.close()
        else:
            self.database.save_message(self.current_chat, 'out', message_text)
            LOGGER.debug(f'Sent a message to {self.current_chat}: {message_text}')
            self.history_list_update()

    # Слот приёма нового сообщений
    @pyqtSlot(dict)
    def message(self, message):
        """
        Слот обработчик поступаемых сообщений. Выполняет дешифровку
        поступаемых сообщений и их сохранение в истории сообщений.
        Запрашивает пользователя, если пришло сообщение не от текущего
        собеседника. При необходимости меняет собеседника.
        """
        self.setStyleSheet(style.COMMON_THEME)

        encrypted_message = base64.b64decode(message[MESSAGE_TEXT])

        try:
            decrypted_message = self.decrypter.decrypt(encrypted_message)
        except (ValueError, TypeError):
            self.messages.warning(self, 'Error', 'Failed to decode message')
            return

            # Сохраняем сообщение в базу и обновляем историю сообщений или открываем новый чат
        self.database.save_message(self.current_chat, 'in', decrypted_message.decode(ENCODING))

        sender = message[SENDER]
        if sender == self.current_chat:
            self.history_list_update()
        else:
            # Проверим есть ли такой пользователь у нас в контактах:
            if self.database.check_contact(sender):
                # Если есть, спрашиваем о желании открыть с ним чат и открываем при желании
                if self.messages.question(
                        self, 'New message',
                        f'New message received from {sender}, '
                        f'open a chat with him?', QMessageBox.Yes,
                        QMessageBox.No
                ) == QMessageBox.Yes:
                    self.current_chat = sender
                    self.set_active_user()
            else:
                # print('NO')
                # Раз нет, спрашиваем хотим ли добавить юзера в контакты.
                if self.messages.question(
                        self, 'New message',
                        f'New message received from {sender}.\n '
                        f'This user is not in your contacts list.\n'
                        f'Add to contacts and open a chat with him?',
                        QMessageBox.Yes, QMessageBox.No
                ) == QMessageBox.Yes:
                    self.add_contact(sender)
                    self.current_chat = sender
                    self.database.save_message(self.current_chat, 'in', decrypted_message.decode(ENCODING))
                    self.set_active_user()

    # Слот потери соединения
    # выдаёт сообщение об ошибке и завершает работу приложения
    @pyqtSlot()
    def connection_lost(self):
        self.setStyleSheet(style.COMMON_THEME)

        self.messages.warning(self, 'Connection failure', 'Lost connection to server')
        self.close()

    @pyqtSlot()
    def sig_205(self):
        self.setStyleSheet(style.COMMON_THEME)
        # Слот, выполняющий обновление баз данных по команде сервера
        if self.current_chat \
                and not self.database.check_user(self.current_chat):
            self.messages.warning(self, 'Sorry', 'Oops... the companion has been deleted from the server')
            self.set_disabled_input()
            self.current_chat = None
        self.clients_list_update()

    def make_connection(self, trans_obj):
        trans_obj.new_message.connect(self.message)
        trans_obj.connection_lost.connect(self.connection_lost)
        trans_obj.message_205.connect(self.sig_205)
