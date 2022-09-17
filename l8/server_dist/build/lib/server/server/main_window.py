import sys
from PyQt5.QtWidgets import (QHeaderView, QMainWindow, QAction, qApp, QApplication, QLabel, QTableView, QToolBar,
                             QVBoxLayout, QWidget)
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QTimer

from server.stat_window import StatWindow
from server.config_window import ConfigWindow
from server.add_user import RegisterUser
from server.remove_user import DelUserDialog

sys.path.append('../')
from common.qss import style
from common.variables import WIDTH, HEIGHT


class MainWindow(QMainWindow):
    """The main window of the server."""

    def __init__(self, database, server, config, width_window=WIDTH, height_window=HEIGHT):
        super().__init__()
        self.database = database
        self.server = server
        self.config = config
        self.width_window = width_window
        self.height_window = height_window

        # Определяем разрешение монитора
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.width = self.screenRect.width()
        self.height = self.screenRect.height()

        # Размеры диалогового окна
        self.width_window = WIDTH
        self.height_window = HEIGHT

        self.setWindowTitle('Telegram на минималках :: Server')
        self.setStyleSheet(style.COMMON_THEME)
        self.setBaseSize(self.width_window, self.height_window)
        self.move(
            self.width // 2 - self.width_window // 2,
            self.height // 2 - self.height_window // 2,
        )

        self.exit_btn = QAction(QIcon('common/img/exit.png'), 'Exit', self)
        self.exit_btn.setShortcut('Ctrl+Q')
        self.exit_btn.triggered.connect(qApp.quit)

        self.refresh_btn = QAction(QIcon('common/img/refresh_2.png'), 'Refresh', self)

        self.show_history_btn = QAction(QIcon('common/img/history.png'), 'History', self)

        self.config_btn = QAction(QIcon('common/img/preferences.png'), 'Preferences', self)

        self.register_btn = QAction(QIcon('common/img/user_add.png'), 'Registration', self)

        self.remove_btn = QAction(QIcon('common/img/user_remove.png'), 'Delete', self)

        self.toolbar = QToolBar(self)

        self.toolbar.addAction(self.register_btn)
        self.toolbar.addAction(self.remove_btn)
        self.toolbar.addAction(self.refresh_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.show_history_btn)
        self.toolbar.addAction(self.config_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.exit_btn)
        self.toolbar.setStyleSheet(style.TOOLBAR_THEME)

        self.active_clients_table = QTableView(self)
        self.active_clients_table.setStyleSheet(style.TABLE_THEME)
        self.active_clients_table.setShowGrid(False)
        self.active_clients_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.active_clients_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.active_clients_table.setMinimumSize(
            self.width_window,
            self.height_window
        )

        self.timer = QTimer()
        self.timer.timeout.connect(self.create_users_model)
        self.timer.start(1000)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.active_clients_table)

        self.widget = QWidget(self)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.statusBar()
        self.statusBar().showMessage('Server Working')

        self.refresh_btn.triggered.connect(self.create_users_model)
        self.show_history_btn.triggered.connect(self.show_statistics)
        self.config_btn.triggered.connect(self.server_config)
        self.register_btn.triggered.connect(self.reg_user)
        self.remove_btn.triggered.connect(self.rem_user)

        self.show()

    def create_users_model(self):
        """The method that fills the table of active users."""

        users_list = self.database.active_users_list()
        model_list = QStandardItemModel()
        model_list.setHorizontalHeaderLabels(['Client name', 'IP address', 'Port', 'Connection time'])

        for row in users_list:
            user, ip, port, time = row
            user = QStandardItem(user)
            user.setEditable(False)
            ip = QStandardItem(ip)
            ip.setEditable(False)
            port = QStandardItem(str(port))
            port.setEditable(False)
            time = QStandardItem(str(time.replace(microsecond=0)))
            time.setEditable(False)
            model_list.appendRow([user, ip, port, time])

        self.active_clients_table.setModel(model_list)
        # Растягиваем строки под контент
        self.active_clients_table.resizeRowsToContents()
        # Первая колонка "резиновая" - тянется в зависимости от размеров окна (и таблицы)
        self.active_clients_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.active_clients_table.resizeColumnToContents(1)
        self.active_clients_table.resizeColumnToContents(2)
        self.active_clients_table.resizeColumnToContents(3)

    def show_statistics(self):
        """Method that creates a window with customer statistics."""

        global stat_window
        stat_window = StatWindow(self.database)
        stat_window.show()

    def server_config(self):
        """Method that creates a window with server settings."""

        global config_window
        config_window = ConfigWindow(self.config)

    def reg_user(self):
        """The method that creates the user registration window."""

        global reg_window
        reg_window = RegisterUser(self.database, self.server)
        reg_window.show()

    def rem_user(self):
        """The method that creates the window for deleting a user."""

        global rem_window
        rem_window = DelUserDialog(self.database, self.server)
        rem_window.show()
