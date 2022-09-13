import sys
import logging

from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QApplication
from PyQt5.QtCore import Qt

sys.path.append('../')
from client.css import style

LOGGER = logging.getLogger('client')


class DelContactDialog(QDialog):
    def __init__(self, database, width_window=400, height_window=90):
        super().__init__()
        self.database = database

        # Размеры диалогового окна
        self.width_window = width_window
        self.height_window = height_window

        # self.setWindowTitle('Select a contact to delete')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(self.width_window, self.height_window)
        self.setStyleSheet(style.COMMON_THEME)
        # Удаляем диалог, если окно было закрыто преждевременно
        self.setAttribute(Qt.WA_DeleteOnClose)
        # Делаем это окно модальным (т.е. поверх других)
        self.setModal(True)

        self.selector_label = QLabel('Select a contact to delete:', self)
        self.selector_label.setFixedSize(
            self.width_window - 20,
            15,
        )
        self.selector_label.move(10, 10)

        # ====={ COMBOBOX }=====
        self.selector = QComboBox(self)
        self.selector.setStyleSheet(style.COMBOBOX_THEME)
        self.selector.setFixedSize(
            int(self.width_window * 0.6) - 10,
            30,
        )
        self.selector.move(10, 30)

        # заполнитель контактов для удаления
        self.selector.addItems(sorted(self.database.get_contacts()))

        # ====={ DELETE button }=====
        self.del_btn = QPushButton('Delete', self)
        self.del_btn.setStyleSheet(style.DEL_BTN_THEME)
        self.del_btn.setFixedSize(
            self.width_window // 3,
            30,
        )
        self.del_btn.move(
            self.width_window - 10 - self.width_window // 3,
            10,
        )

        # ====={ CANCEL button }=====
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


if __name__ == '__main__':
    app = QApplication(sys.argv)

    from db.client_db_config import ClientDB

    database = ClientDB('test1')
    window = DelContactDialog(database=database)

    database.add_contact('test1')
    database.add_contact('test2')
    print(database.get_contacts())
    window.selector.addItems(sorted(database.get_contacts()))
    window.show()
    app.exec_()
