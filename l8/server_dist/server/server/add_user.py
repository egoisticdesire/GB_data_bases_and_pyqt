import binascii
import hashlib
import sys
import logging

from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QLineEdit, QMessageBox, QPushButton, QApplication
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon

from common.variables import ENCODING

sys.path.append('../')
from common.qss import style

LOGGER = logging.getLogger('server')


class RegisterUser(QDialog):
    """The user registration dialog class on the server."""
    def __init__(self, database, server, width_window=300, height_window=400):
        super().__init__()
        self.database = database
        self.server = server
        self.width_window = width_window
        self.height_window = height_window

        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.width = self.screenRect.width()
        self.height = self.screenRect.height()

        self.setWindowTitle('User registration')
        self.setStyleSheet(style.COMMON_THEME)
        self.setFixedSize(self.width_window, self.height_window)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)
        self.move(
            self.width // 2 - self.width_window // 2,
            self.height // 2 - self.height_window // 2,
        )

        self.username_label = QLabel('Username:', self)
        self.username_label.move(10, 10)
        self.username_label.setFixedSize(
            self.width_window - 20,
            20,
        )

        self.client_name = QLineEdit(self)
        self.client_name.setStyleSheet(style.INPUT_NAME_THEME)
        self.client_name.setPlaceholderText('Username must be at least 3 characters')
        self.client_name.move(10, 35)
        self.client_name.setFixedSize(
            self.width_window - 20,
            30,
        )

        self.name_hidden_label = QLabel('*incorrect username!', self)
        self.name_hidden_label.setStyleSheet(style.HIDDEN_LABEL_THEME)
        self.name_hidden_label.setVisible(False)
        self.name_hidden_label.move(10, 70)
        self.name_hidden_label.setFixedSize(
            self.width_window - 20,
            15,
        )
        self.name_not_three_hidden_label = QLabel('*name must be at least 3 characters', self)
        self.name_not_three_hidden_label.setStyleSheet(style.HIDDEN_LABEL_THEME)
        self.name_not_three_hidden_label.setVisible(False)
        self.name_not_three_hidden_label.move(10, 70)
        self.name_not_three_hidden_label.setFixedSize(
            self.width_window - 20,
            15,
        )

        self.password_label = QLabel('Password:', self)
        self.password_label.move(10, 90)
        self.password_label.setFixedSize(
            self.width_window - 20,
            20,
        )

        self.client_pswd = QLineEdit(self)
        self.client_pswd.setStyleSheet(style.INPUT_NAME_THEME)
        self.client_pswd.setPlaceholderText('Password must be at least 8 characters')
        self.client_pswd.move(10, 115)
        self.client_pswd.setFixedSize(
            self.width_window - 20,
            30,
        )
        self.client_pswd.setEchoMode(QLineEdit.Password)

        self.pswd_hidden_label = QLabel('*incorrect password!', self)
        self.pswd_hidden_label.setStyleSheet(style.HIDDEN_LABEL_THEME)
        self.pswd_hidden_label.setVisible(False)
        self.pswd_hidden_label.move(10, 150)
        self.pswd_hidden_label.setFixedSize(
            self.width_window - 20,
            15,
        )

        self.pswd_not_eight_hidden_label = QLabel('*password must be at least 8 characters', self)
        self.pswd_not_eight_hidden_label.setStyleSheet(style.HIDDEN_LABEL_THEME)
        self.pswd_not_eight_hidden_label.setVisible(False)
        self.pswd_not_eight_hidden_label.move(10, 150)
        self.pswd_not_eight_hidden_label.setFixedSize(
            self.width_window - 20,
            15,
        )

        self.confirm_label = QLabel('Confirm:', self)
        self.confirm_label.move(10, 170)
        self.confirm_label.setFixedSize(
            self.width_window - 20,
            20,
        )

        self.client_conf = QLineEdit(self)
        self.client_conf.setStyleSheet(style.INPUT_NAME_THEME)
        self.client_conf.setPlaceholderText('Password confirmation')
        self.client_conf.move(10, 195)
        self.client_conf.setFixedSize(
            self.width_window - 20,
            30,
        )
        self.client_conf.setEchoMode(QLineEdit.Password)

        self.conf_hidden_label = QLabel('*incorrect password confirmation!', self)
        self.conf_hidden_label.setStyleSheet(style.HIDDEN_LABEL_THEME)
        self.conf_hidden_label.setVisible(False)
        self.conf_hidden_label.move(10, 230)
        self.conf_hidden_label.setFixedSize(
            self.width_window - 20,
            15,
        )

        self.ok_btn = QPushButton('Accept', self)
        self.ok_btn.setStyleSheet(style.OK_BTN_THEME)
        self.ok_btn.setFixedSize(
            self.width_window - 20,
            37,
        )
        self.ok_btn.move(
            10,
            self.height_window - 10 - 37 - 10 - 37  # высота окна - отступ - кнопка - отступ - кнопка
        )
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self.save_data)

        self.exit_btn = QPushButton('Exit', self)
        self.exit_btn.setStyleSheet(style.EXIT_BTN_THEME)
        self.exit_btn.setFixedSize(
            self.width_window - 20,
            37,
        )
        self.exit_btn.move(
            10,
            self.height_window - 10 - 37  # высота окна - отступ - кнопка
        )
        self.exit_btn.clicked.connect(self.close)

        self.messages = QMessageBox()

        self.show()

    def save_data(self):
        """A method for checking the correctness of entering and saving a new user to the database."""

        # Проверка корректности имени
        # Если содержатся пробелы - выводим скрытое поле
        if ' ' in self.client_name.text():
            self.name_hidden_label.setVisible(True)
            self.name_not_three_hidden_label.setVisible(False)
        # Если длина имени меньше 3 символов - выводим другое скрытое поле
        elif len(self.client_name.text()) < 3:
            self.name_hidden_label.setVisible(False)
            self.name_not_three_hidden_label.setVisible(True)
        # Иначе прячем все скрытые поля
        else:
            self.name_hidden_label.setVisible(False)
            self.name_not_three_hidden_label.setVisible(False)

        # Проверка корректности пароля
        if ' ' in self.client_pswd.text():
            self.pswd_hidden_label.setVisible(True)
            self.pswd_not_eight_hidden_label.setVisible(False)
        elif len(self.client_pswd.text()) < 8:
            self.pswd_hidden_label.setVisible(False)
            self.pswd_not_eight_hidden_label.setVisible(True)
        else:
            self.pswd_hidden_label.setVisible(False)
            self.pswd_not_eight_hidden_label.setVisible(False)

        # Проверка подтверждения пароля
        if self.client_pswd.text() != self.client_conf.text():
            self.conf_hidden_label.setVisible(True)
        else:
            self.conf_hidden_label.setVisible(False)

        # Если все условия выполнены - добавляем пользователя в базу данных
        if not len(self.client_name.text()) < 3 \
                and ' ' not in self.client_name.text() \
                and not len(self.client_pswd.text()) < 8 \
                and ' ' not in self.client_pswd.text() \
                and self.client_pswd.text() == self.client_conf.text():
            pswd_bytes = self.client_pswd.text().encode(ENCODING)
            salt = self.client_name.text().lower().encode(ENCODING)
            pswd_hash = hashlib.pbkdf2_hmac('sha512', pswd_bytes, salt, 10000)
            self.database.add_user(self.client_name.text(), binascii.hexlify(pswd_hash))
            self.messages.information(self, 'Success', 'User successfully registered')
            self.server.service_update_lists()
            self.close()

        # Если пользователь с таким именем существует - уведомляем об этом
        elif self.database.check_user(self.client_name.text()):
            self.messages.critical(
                self, 'Error', 'User already exists'
            )
            return


if __name__ == '__main__':
    app = QApplication([])
    from db.server_db_config import ServerDB

    database = ServerDB('../db/server_db.db3')
    import os
    import sys

    path1 = os.path.join(os.getcwd(), '..')
    sys.path.insert(0, path1)
    from core import MessageProcessor

    server = MessageProcessor('127.0.0.1', 7777, database)
    dial = RegisterUser(database, server)
    app.exec_()
