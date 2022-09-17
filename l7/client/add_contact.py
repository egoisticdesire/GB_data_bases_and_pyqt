import sys
import logging

from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon

sys.path.append('../')
from common.qss import style

LOGGER = logging.getLogger('client')


class AddContactDialog(QDialog):
    """
    Dialog for adding a user to the contact list.
    Offers the user a list of possible contacts
    and adds the selected one to contacts.
    """

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
        self.setAttribute(Qt.WA_DeleteOnClose)
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
        self.refresh_btn.setIcon(QIcon('common/img/refresh_2.png'))
        self.refresh_btn.setIconSize(QSize(25, 25))
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
        """
        Method for filling list of possible contacts.
        Creates a list of all registered users,
        excluding those already added to contacts and himself.
        """
        self.selector.clear()
        # множества всех контактов и контактов клиента
        contacts_list = set(self.database.get_contacts())
        users_list = set(self.database.get_users())
        # Удалим сами себя из списка пользователей, чтобы нельзя было добавить самого себя
        users_list.remove(self.transport.username)
        # Добавляем список возможных контактов
        self.selector.addItems(users_list - contacts_list)

    def upd_possible_contacts(self):
        """
        Method for updating the list of possible contacts.
        Requests a list of known users from the server
        and updates the contents of the window.
        """
        try:
            self.transport.user_list_update()
        except OSError:
            pass
        else:
            LOGGER.debug('Updating the list of users from the server is done')
            self.possible_contacts_update()
