import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QHeaderView, QTableView,
                             QVBoxLayout)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

sys.path.append('../')
from common.qss import style
from common.qss.animated_close_btn import AnimatedClosePushButton


class StatWindow(QDialog):
    """User statistics window"""

    def __init__(self, database):
        super().__init__()
        self.layout = None
        self.desktop = None
        self.screenRect = None
        self.width = None
        self.height = None
        self.width_window = None
        self.height_window = None
        self.stat_table = None
        self.close_btn = None
        self.database = database
        self.initUI()

    def initUI(self):
        # Определяем разрешение монитора
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.width = self.screenRect.width()
        self.height = self.screenRect.height()

        # Размеры диалогового окна
        self.width_window = self.width // 4
        self.height_window = self.height // 3

        self.setWindowTitle('Client statistics')
        self.setStyleSheet(style.COMMON_THEME)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setBaseSize(self.width_window, self.height_window)
        self.move(
            self.width // 2 - self.width_window // 2,
            self.height // 2 - self.height_window // 2,
        )

        self.close_btn = AnimatedClosePushButton()
        self.close_btn.setText('Close')
        # self.close_btn.setStyleSheet(style.CANCEL_BTN_THEME)
        self.close_btn.setFixedHeight(25)
        self.close_btn.clicked.connect(self.close)

        self.stat_table = QTableView(self)
        self.stat_table.setStyleSheet(style.TABLE_THEME)
        self.stat_table.setShowGrid(False)
        self.stat_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.stat_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.stat_table.setMinimumSize(
            self.width_window,
            self.height_window
        )

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.close_btn)
        self.layout.addWidget(self.stat_table)

        self.create_stat_model()

    def create_stat_model(self):
        """The method that implements filling the table with message statistics."""

        stat_list = self.database.message_history()

        model_list = QStandardItemModel()
        model_list.setHorizontalHeaderLabels(['Client name', 'Last activity', 'Sent', 'Received'])

        for row in stat_list:
            user, last_seen, sent, recvd = row
            user = QStandardItem(user)
            user.setEditable(False)
            last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
            last_seen.setEditable(False)
            sent = QStandardItem(str(sent))
            sent.setEditable(False)
            recvd = QStandardItem(str(recvd))
            recvd.setEditable(False)
            model_list.appendRow([user, last_seen, sent, recvd])

        self.stat_table.setModel(model_list)

        # Растягиваем строки под контент
        self.stat_table.resizeRowsToContents()
        # Первая колонка "резиновая" - тянется в зависимости от размеров окна (и таблицы)
        self.stat_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # Вторая колонка растягивается автоматически под контент
        self.stat_table.resizeColumnToContents(1)
        # Две колонки с фиксированной шириной
        self.stat_table.horizontalHeader().resizeSection(0, self.stat_table.width() // 4)
        self.stat_table.horizontalHeader().resizeSection(0, self.stat_table.width() // 4)


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
    dial = StatWindow(database)
    dial.show()
    app.exec_()
