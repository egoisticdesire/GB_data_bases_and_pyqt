import sys
import logging

from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QApplication
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon

sys.path.append('../')
from client.css import style

LOGGER = logging.getLogger('client')


class AddContactDialog(QDialog):
    def __init__(self, transport, database, width_window=400, height_window=90):
        self.transport = transport
        self.database = database
        super().__init__()

        # Размеры диалогового окна
        self.width_window = width_window
        self.height_window = height_window

        # self.setWindowTitle('Select a contact to invite')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(self.width_window, self.height_window)
        self.setStyleSheet(style.COMMON_THEME)
        # Удаляем диалог, если окно было закрыто преждевременно
        self.setAttribute(Qt.WA_DeleteOnClose)
        # Делаем это окно модальным (т.е. поверх других)
        self.setModal(True)

        self.selector_label = QLabel('Select a contact to invite:', self)
        self.selector_label.setFixedSize(
            self.width_window - 20,
            15,
        )
        self.selector_label.move(10, 10)

        # ====={ COMBOBOX }=====
        self.selector = QComboBox(self)
        self.selector.setStyleSheet(style.COMBOBOX_THEME)
        self.selector.setFixedSize(
            self.width_window // 2 - 10,
            30,
        )
        self.selector.move(10, 30)

        # ====={ REFRESH button }=====
        self.refresh_btn = QPushButton(self)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setToolTip('Refresh')
        self.refresh_btn.setIcon(QIcon('client/img/refresh.png'))
        self.refresh_btn.setIconSize(QSize(30, 30))
        self.refresh_btn.setStyleSheet(style.NONE_BORDER_BGCOLOR_BTN_THEME)
        self.refresh_btn.setFixedSize(30, 30)
        self.refresh_btn.move(
            self.width_window // 2 + 10,
            30,
        )

        # ====={ ADD button }=====
        self.add_btn = QPushButton('Add', self)
        self.add_btn.setDefault(True)
        self.add_btn.setStyleSheet(style.OK_BTN_THEME)
        self.add_btn.setFixedSize(
            self.width_window // 3,
            30,
        )
        self.add_btn.move(
            self.width_window - 10 - self.width_window // 3,
            10,
        )

        # ====={ CANCEL button }=====
        self.cancel_btn = QPushButton('Cancel', self)
        self.cancel_btn.setStyleSheet(style.CANCEL_BTN_THEME)
        self.cancel_btn.clicked.connect(self.close)
        self.cancel_btn.setFixedSize(
            self.width_window // 3,
            30,
        )
        self.cancel_btn.move(
            self.width_window - 10 - self.width_window // 3,
            10 + 30 + 10,  # отступ сверху + высота кнопки + отступ от кнопки
        )

        # Заполняем список возможных контактов
        self.possible_contacts_update()
        # Назначаем действие на кнопку обновить
        self.refresh_btn.clicked.connect(self.upd_possible_contacts)

    # Заполняем список возможных контактов разницей между всеми пользователями и
    def possible_contacts_update(self):
        self.selector.clear()
        # множества всех контактов и контактов клиента
        contacts_list = set(self.database.get_contacts())
        users_list = set(self.database.get_users())
        # Удалим сами себя из списка пользователей, чтобы нельзя было добавить самого себя
        users_list.remove(self.transport.username)
        # Добавляем список возможных контактов
        self.selector.addItems(users_list - contacts_list)

    # Обновляет таблицу известных пользователей (забирает с сервера),
    # затем содержимое предполагаемых контактов
    def upd_possible_contacts(self):
        try:
            self.transport.user_list_update()
        except OSError:
            pass
        else:
            LOGGER.debug('Updating the list of users from the server is done')
            self.possible_contacts_update()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    from db.client_db_config import ClientDB

    database = ClientDB('test1')

    from transport import ClientTransport

    transport = ClientTransport('127.0.0.1', 7777, database, 'test1')

    window = AddContactDialog(transport=transport, database=database)
    window.show()
    app.exec_()
