import sys

from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel, qApp

sys.path.append('../')
from common.qss import style


class UsernameDialog(QDialog):
    """Implements a start dialog asking for the user's login and password."""

    def __init__(self, width_window=300, height_window=200):
        super().__init__()
        self.ok_pressed = False

        # Размеры диалогового окна
        self.width_window = width_window
        self.height_window = height_window

        # Определяем разрешение монитора
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.width = self.screenRect.width()
        self.height = self.screenRect.height()

        self.setWindowTitle('Welcome!')
        self.setFixedSize(self.width_window, self.height_window)
        self.setStyleSheet(style.COMMON_THEME)

        # Двигаем диалоговое окно в центр монитора
        # и смещаем на половину его ширины и высоты
        self.move(
            self.width // 2 - self.width_window // 2,
            self.height // 2 - self.height_window // 2,
        )

        # Создаем лейбл, задаем размеры
        # self.label = QLabel('Username:', self)
        # self.label.setFixedSize(
        #     self.width_window - 20,
        #     20,
        # )
        # self.label.move(10, 10)

        # Создаем скрытый лейбл для имени, задаем размеры
        self.name_hidden_label = QLabel('*incorrect username!', self)
        self.name_hidden_label.setStyleSheet(style.HIDDEN_LABEL_THEME)
        self.name_hidden_label.setVisible(False)
        self.name_hidden_label.setFixedSize(
            self.width_window - 20,
            15,
        )
        self.name_hidden_label.move(10, 50)

        # Создаем скрытый лейбл для пароля, задаем размеры
        self.pswd_hidden_label = QLabel('*incorrect password!', self)
        self.pswd_hidden_label.setStyleSheet(style.HIDDEN_LABEL_THEME)
        self.pswd_hidden_label.setVisible(False)
        self.pswd_hidden_label.setFixedSize(
            self.width_window - 20,
            15,
        )
        self.pswd_hidden_label.move(10, 110)

        # Создаем строку для ввода имени пользователя, задаем размеры
        self.client_name = QLineEdit(self)
        self.client_name.setStyleSheet(style.INPUT_NAME_THEME)
        self.client_name.setPlaceholderText('Username')
        self.client_name.setFixedSize(
            self.width_window - 20,
            30,
        )
        self.client_name.move(10, 15)

        # self.label_passwd = QLabel('Password:', self)
        # self.label_passwd.move(10, 55)
        # self.label_passwd.setFixedSize(150, 15)

        self.client_pswd = QLineEdit(self)
        self.client_pswd.setEchoMode(QLineEdit.Password)
        self.client_pswd.setStyleSheet(style.INPUT_NAME_THEME)
        self.client_pswd.setPlaceholderText('Password')
        self.client_pswd.setFixedSize(
            self.width_window - 20,
            30
        )
        self.client_pswd.move(10, 75)

        # Создаем кнопку ОК, задаем размеры
        self.ok_btn = QPushButton('Accept', self)
        self.ok_btn.setDefault(True)
        self.ok_btn.setStyleSheet(style.OK_BTN_THEME)
        self.ok_btn.clicked.connect(self.click)
        self.ok_btn.setFixedSize(
            self.width_window // 2 - 15,
            37,
        )
        self.ok_btn.move(
            10,
            self.height_window - 10 - 37,  # (высота окна - отступ - высота кнопки), для привязки к нижней границе
        )

        # Создаем кнопку ВЫХОД, задаем размеры
        self.exit_btn = QPushButton('Exit', self)
        self.exit_btn.setStyleSheet(style.EXIT_BTN_THEME)
        self.exit_btn.clicked.connect(qApp.exit)
        self.exit_btn.setFixedSize(
            self.width_window // 2 - 15,
            37,
        )
        self.exit_btn.move(
            self.width_window // 2 + 5,
            self.height_window - 10 - 37,  # (высота окна - отступ - высота кнопки), для привязки к нижней границе
        )

        self.show()

    def click(self):
        """'OK' button handler"""
        self.name_hidden_label.setVisible(
            False if self.client_name.text() and ' ' not in self.client_name.text() else True
        )

        self.pswd_hidden_label.setVisible(
            False if self.client_pswd.text() and ' ' not in self.client_pswd.text() else True
        )

        # проверяем, введено ли имя
        # запрещаем имя, если оно содержит пробелы
        if self.client_name.text() \
                and self.client_pswd.text() \
                and ' ' not in self.client_name.text() \
                and ' ' not in self.client_pswd.text():
            self.ok_pressed = True
            qApp.exit()


if __name__ == '__main__':
    app = QApplication([])
    dialog = UsernameDialog()
    app.exec_()
