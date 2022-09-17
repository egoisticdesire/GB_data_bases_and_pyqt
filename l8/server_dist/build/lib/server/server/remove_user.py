import sys
import logging
from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QApplication
from PyQt5.QtCore import Qt

sys.path.append('../')
from common.qss import style

LOGGER = logging.getLogger('server')


class DelUserDialog(QDialog):
    """Dialog for selecting a contact to delete."""

    def __init__(self, database, server, width_window=400, height_window=90):
        super().__init__()
        self.database = database
        self.server = server
        self.width_window = width_window
        self.height_window = height_window

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(self.width_window, self.height_window)
        self.setStyleSheet(style.COMMON_THEME)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Select a user to delete:', self)
        self.selector_label.setFixedSize(
            self.width_window - 20,
            15,
        )
        self.selector_label.move(10, 10)

        self.selector = QComboBox(self)
        self.selector.setStyleSheet(style.COMBOBOX_THEME)
        self.selector.setFixedSize(
            int(self.width_window * 0.6) - 10,
            30,
        )
        self.selector.move(10, 30)

        self.del_btn = QPushButton('Delete', self)
        self.del_btn.setStyleSheet(style.DEL_BTN_THEME)
        self.del_btn.clicked.connect(self.remove_user)
        self.del_btn.setFixedSize(
            self.width_window // 3,
            30,
        )
        self.del_btn.move(
            self.width_window - 10 - self.width_window // 3,
            10,
        )

        self.cancel_btn = QPushButton('Cancel', self)
        self.cancel_btn.setStyleSheet(style.CANCEL_BTN_THEME)
        self.cancel_btn.setDefault(True)
        self.cancel_btn.clicked.connect(self.close)
        self.cancel_btn.setFixedSize(
            self.width_window // 3,
            30,
        )
        self.cancel_btn.move(
            self.width_window - 10 - self.width_window // 3,
            10 + 30 + 10,  # отступ сверху + высота кнопки + отступ от кнопки
        )

        self.all_users_fill()

    def all_users_fill(self):
        """The method that populates the list of users."""

        self.selector.addItems([item[0] for item in self.database.users_list()])

    def remove_user(self):
        """User deletion handler method."""

        self.database.remove_user(self.selector.currentText())
        if self.selector.currentText() in self.server.names:
            sock = self.server.names[self.selector.currentText()]
            del self.server.names[self.selector.currentText()]
            self.server.remove_client(sock)
        # Рассылаем клиентам сообщение о необходимости обновить справочники
        self.server.service_update_lists()
        self.close()


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
    dial = DelUserDialog(database, server)
    dial.show()
    app.exec_()
