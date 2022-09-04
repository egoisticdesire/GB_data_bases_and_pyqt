import sys
from PyQt5.QtWidgets import (QMainWindow, QAction, qApp, QApplication, QLabel, QTableView, QDialog, QPushButton,
                             QLineEdit, QFileDialog)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

from common.variables import HEIGHT, WIDTH


# GUI - Создание таблицы QModel, для отображения в окне программы.
def gui_create_model(database):
    users_list = database.active_users_list()
    table_list = QStandardItemModel()
    table_list.setHorizontalHeaderLabels(['Client', 'IP address', 'Port', 'Connection time'])

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

        table_list.appendRow([user, ip, port, time])

    return table_list


# GUI - Функция реализующая заполнение таблицы историей сообщений.
def create_stat_model(database):
    # Список записей из базы
    hist_list = database.message_history()

    # Объект модели данных:
    table_list = QStandardItemModel()
    table_list.setHorizontalHeaderLabels(['Client', 'Last activity', 'Messages sent', 'Messages received'])

    for row in hist_list:
        user, last_seen, sent, recvd = row
        user = QStandardItem(user)
        user.setEditable(False)
        last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
        last_seen.setEditable(False)
        sent = QStandardItem(str(sent))
        sent.setEditable(False)
        recvd = QStandardItem(str(recvd))
        recvd.setEditable(False)
        table_list.appendRow([user, last_seen, sent, recvd])
    return table_list


class MainWindow(QMainWindow):
    def __init__(self, width_window=WIDTH, height_window=HEIGHT):
        super().__init__()
        self.active_clients_table = None
        self.label = None
        self.toolbar = None
        self.config_btn = None
        self.show_history_btn = None
        self.refresh_btn = None
        self.exit_btn = None
        self.width_window = width_window
        self.height_window = height_window
        self.initUI()

    def initUI(self):
        self.exit_btn = QAction('Exit', self)
        self.exit_btn.setShortcut('Escape')
        self.exit_btn.triggered.connect(qApp.quit)

        self.refresh_btn = QAction('Refresh', self)

        self.show_history_btn = QAction('History', self)

        self.config_btn = QAction('Preferences', self)

        self.statusBar()

        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(self.exit_btn)
        self.toolbar.addAction(self.refresh_btn)
        self.toolbar.addAction(self.show_history_btn)
        self.toolbar.addAction(self.config_btn)

        self.setFixedSize(self.width_window, self.height_window)
        self.setWindowTitle('Telegram на минималках :: Server')

        self.label = QLabel('List of connected clients: ', self)
        self.label.setFixedSize(400, 15)
        self.label.move(10, 35)

        self.active_clients_table = QTableView(self)
        self.active_clients_table.setFixedSize(780, 400)
        self.active_clients_table.move(10, 55)

        self.show()


class HistoryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.history_table = None
        self.close_btn = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Clients statistics')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_btn = QPushButton('Close', self)
        self.close_btn.move(250, 650)
        self.close_btn.clicked.connect(self.close)

        self.history_table = QTableView(self)
        self.history_table.setFixedSize(580, 620)
        self.history_table.move(10, 10)

        self.show()


class ConfigWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.close_btn = None
        self.save_btn = None
        self.ip = None
        self.ip_label_note = None
        self.ip_label = None
        self.port = None
        self.port_label = None
        self.db_file = None
        self.db_file_label = None
        self.db_path_select = None
        self.db_path = None
        self.db_path_label = None
        self.initUI()

    def initUI(self):
        # Настройки окна
        self.setFixedSize(365, 360)
        self.setWindowTitle('Server settings')

        # Надпись о файле базы данных:
        self.db_path_label = QLabel('Path to the database file: ', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        # Строка с путём базы
        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 27)
        self.db_path.move(10, 28)
        self.db_path.setReadOnly(True)

        # Кнопка выбора пути.
        self.db_path_select = QPushButton('Browse...', self)
        self.db_path_select.move(275, 28)

        # Функция обработчик открытия окна выбора папки
        def open_file_dialog():
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            path = path.replace('/', '\\')
            self.db_path.insert(path)

        self.db_path_select.clicked.connect(open_file_dialog)

        # Метка с именем поля файла базы данных
        self.db_file_label = QLabel('Database file name: ', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)

        # Поле для ввода имени файла
        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150, 20)

        # Метка с номером порта
        self.port_label = QLabel('Port number for connections:', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        # Поле для ввода номера порта
        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        # Метка с адресом для соединений
        self.ip_label = QLabel('From which IP to accept\nconnections:', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(150, 40)

        # Метка с напоминанием о пустом поле.
        self.ip_label_note = QLabel('*leave this field blank to\naccept connections from any addresses.', self)
        self.ip_label_note.move(10, 198)
        self.ip_label_note.setFixedSize(500, 40)

        # Поле для ввода ip
        self.ip = QLineEdit(self)
        self.ip.move(200, 158)
        self.ip.setFixedSize(150, 20)

        # Кнопка сохранения настроек
        self.save_btn = QPushButton('Save', self)
        self.save_btn.move(190, 320)

        # Кнопка закрытия окна
        self.close_btn = QPushButton('Close', self)
        self.close_btn.move(275, 320)
        self.close_btn.clicked.connect(self.close)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.statusBar().showMessage('Test Statusbar Message')
    test_list = QStandardItemModel(main_window)
    test_list.setHorizontalHeaderLabels(['Client', 'IP address', 'Port', 'Connection time'])
    test_list.appendRow(
        [QStandardItem('test1'), QStandardItem('192.198.0.5'), QStandardItem('23544'), QStandardItem('16:20:34')]
    )
    test_list.appendRow(
        [QStandardItem('test2'), QStandardItem('192.198.0.8'), QStandardItem('33245'), QStandardItem('16:22:11')]
    )
    main_window.active_clients_table.setModel(test_list)
    main_window.active_clients_table.resizeColumnsToContents()
    app.exec_()

    # ----------------------------------------------------------

    # app = QApplication(sys.argv)
    # window = HistoryWindow()
    # test_list = QStandardItemModel(window)
    # test_list.setHorizontalHeaderLabels(
    #     ['Имя Клиента', 'Последний раз входил', 'Отправлено', 'Получено'])
    # test_list.appendRow(
    #     [QStandardItem('test1'), QStandardItem('Fri Dec 12 16:20:34 2020'), QStandardItem('2'), QStandardItem('3')])
    # test_list.appendRow(
    #     [QStandardItem('test2'), QStandardItem('Fri Dec 12 16:23:12 2020'), QStandardItem('8'), QStandardItem('5')])
    # window.history_table.setModel(test_list)
    # window.history_table.resizeColumnsToContents()
    #
    # app.exec_()

    # ----------------------------------------------------------

    # app = QApplication(sys.argv)
    # dial = ConfigWindow()
    #
    # app.exec_()
