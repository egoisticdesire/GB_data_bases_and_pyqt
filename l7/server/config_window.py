import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import QSize, Qt

sys.path.append('../')
from common.qss import style


class ConfigWindow(QDialog):
    """Settings window."""

    def __init__(self, config):
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
        self.config = config
        self.width_window = None
        self.height_window = None
        self.indent = 10
        self.initUI()

    def initUI(self):
        # Определяем разрешение монитора
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.width = self.screenRect.width()
        self.height = self.screenRect.height()

        # Размеры диалогового окна
        self.width_window = 550
        self.height_window = 400

        self.setWindowTitle('Server settings')
        self.setFixedSize(self.width_window, self.height_window)
        self.setStyleSheet(style.COMMON_THEME)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.db_path_label = QLabel('Path to the database file: ', self)
        self.db_path_label.move(self.indent, self.indent)
        self.db_path_label.setFixedSize(
            self.width_window - self.indent,
            20
        )

        self.db_path = QLineEdit(self)
        self.db_path.setStyleSheet(style.DISABLED_INPUT_NAME_THEME)
        self.db_path.setReadOnly(True)
        self.db_path.move(
            self.indent,
            self.indent + self.db_path_label.height()
        )
        self.db_path.setFixedSize(
            self.width_window - self.indent * 2,
            30
        )

        self.db_path_select = QPushButton(self)

        self.db_path_select.setCursor(Qt.PointingHandCursor)
        self.db_path_select.setToolTip('Choice a path of database file')
        self.db_path_select.setIcon(QIcon('common/img/search_folder_2.png'))
        self.db_path_select.setIconSize(QSize(25, 25))
        self.db_path_select.setStyleSheet(style.NONE_BORDER_BGCOLOR_BTN_THEME)

        self.db_path_select.setDefault(True)
        self.db_path_select.move(
            self.width_window - self.indent * 4,
            30
        )
        self.db_path_select.setFixedSize(30, 30)

        self.db_file_label = QLabel('Database file name: ', self)
        self.db_file_label.move(
            self.indent,
            self.indent * 2 + self.db_path_label.height() + self.db_path.height()
        )
        self.db_file_label.setFixedSize(
            self.width_window // 2,
            30
        )

        self.db_file = QLineEdit(self)
        self.db_file.setStyleSheet(style.INPUT_NAME_THEME)
        self.db_file.move(
            self.width_window - self.db_file_label.width(),
            self.indent * 2 + self.db_path_label.height() + self.db_path.height()
        )
        self.db_file.setFixedSize(
            self.width_window // 2 - self.indent,
            30
        )

        self.port_label = QLabel('Port number for connections:', self)
        self.port_label.move(
            self.indent,
            self.indent * 3 + self.db_path_label.height() + self.db_path.height() + self.db_file_label.height()
        )
        self.port_label.setFixedSize(
            self.width_window // 2,
            30
        )

        self.port = QLineEdit(self)
        self.port.setStyleSheet(style.INPUT_NAME_THEME)
        self.port.move(
            self.width_window - self.db_file_label.width(),
            self.indent * 3 + self.db_path_label.height() + self.db_path.height() + self.db_file_label.height()
        )
        self.port.setFixedSize(
            self.width_window // 2 - self.indent,
            30
        )

        self.ip_label = QLabel('From which IP we accept connections:', self)
        self.ip_label.move(
            self.indent,
            self.indent * 4 + self.db_path_label.height() + self.db_path.height() + self.db_file_label.height() + self.port_label.height()
        )
        self.ip_label.setFixedSize(
            self.width_window // 2,
            30
        )

        self.ip_label_note = QLabel('*leave this field blank to accept connections from any address', self)
        self.ip_label_note.setWordWrap(True)
        self.ip_label_note.setStyleSheet('font-size: 13px;')
        self.ip_label_note.move(
            self.indent,
            self.indent * 4 + self.db_path_label.height() + self.db_path.height() + self.db_file_label.height() + self.port_label.height() + self.ip_label.height()
        )
        self.ip_label_note.setFixedSize(
            self.width_window // 2 - self.indent * 2,
            30
        )

        self.ip = QLineEdit(self)
        self.ip.setStyleSheet(style.INPUT_NAME_THEME)
        self.ip.move(
            self.width_window - self.ip_label.width(),
            self.indent * 4 + self.db_path_label.height() + self.db_path.height() + self.db_file_label.height() + self.port_label.height()
        )
        self.ip.setFixedSize(
            self.width_window // 2 - self.indent,
            30
        )

        self.save_btn = QPushButton('Save and close', self)
        self.save_btn.setStyleSheet(style.OK_BTN_THEME)
        self.save_btn.move(
            self.indent,
            self.height_window - self.save_btn.height() - self.indent * 2
        )
        self.save_btn.setFixedSize(
            self.width_window // 3 * 2 - self.indent,
            40
        )

        self.close_btn = QPushButton('Close', self)
        self.close_btn.setStyleSheet(style.CANCEL_BTN_THEME)
        self.close_btn.move(
            self.save_btn.width() + self.indent * 2,
            self.height_window - self.close_btn.height() - self.indent * 2
        )
        self.close_btn.setFixedSize(
            self.width_window - self.save_btn.width() - self.indent * 3,
            40
        )
        self.close_btn.clicked.connect(self.close)

        self.db_path_select.clicked.connect(self.open_file_dialog)

        self.show()

        self.db_path.insert(self.config['SETTINGS']['Database_path'])
        self.db_file.insert(self.config['SETTINGS']['Database_file'])
        self.port.insert(self.config['SETTINGS']['Default_port'])
        self.ip.insert(self.config['SETTINGS']['Listen_Addr'])
        self.save_btn.clicked.connect(self.save_server_config)

    def open_file_dialog(self):
        """Handler method for opening the folder selection window."""

        global dialog
        dialog = QFileDialog(self)
        path = dialog.getExistingDirectory().replace('/', '\\')
        self.db_path.clear()
        self.db_path.insert(path)

    def save_server_config(self):
        """
        Method for saving settings.
        Checks the correctness of the entered data
        and if everything correct saves the ini file.
        """

        global config_window
        message = QMessageBox()
        self.config['SETTINGS']['Database_path'] = self.db_path.text()
        self.config['SETTINGS']['Database_file'] = self.db_file.text()

        try:
            port = int(self.port.text())
        except ValueError:
            message.warning(self, 'Error', 'Port must be a number')
        else:
            self.config['SETTINGS']['Listen_Addr'] = self.ip.text()

            if 1023 < port < 65536:
                self.config['SETTINGS']['Default_port'] = str(port)
                dir_path = os.path.dirname(os.path.realpath(__file__))
                dir_path = os.path.join(dir_path, '..')
                with open(f'{dir_path}/server/server.ini', 'w') as conf:
                    self.config.write(conf)
                    message.information(self, 'OK', 'Settings successfully saved!')
            else:
                message.warning(self, 'Error', 'Port must be between 1024 and 65536')

            self.close()
