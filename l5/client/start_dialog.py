import sys

from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel, qApp

sys.path.append('../')
from client.css import style


class UsernameDialog(QDialog):
    def __init__(self, width_window=300, height_window=150):
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
        self.label = QLabel('Enter username:', self)
        self.label.setFixedSize(
            self.width_window - 20,
            20,
        )
        self.label.move(10, 10)

        # Создаем скрытый лейбл, задаем размеры
        self.hidden_label = QLabel('*incorrect username!', self)
        self.hidden_label.setStyleSheet(style.HIDDEN_LABEL_THEME)
        self.hidden_label.setVisible(False)
        self.hidden_label.setFixedSize(
            self.width_window - 20,
            15,
        )
        self.hidden_label.move(10, 70)

        # Создаем строку для ввода имени пользователя, задаем размеры
        self.client_name = QLineEdit(self)
        self.client_name.setStyleSheet(style.INPUT_NAME_THEME)
        self.client_name.setPlaceholderText('Username')
        self.client_name.setFixedSize(
            self.width_window - 20,
            30,
        )
        self.client_name.move(10, 35)

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
        # проверяем, введено ли имя
        # запрещаем имя, если оно начинается с пробелов или заканчивается пробелами
        if self.client_name.text() \
                and not self.client_name.text().startswith(' ') \
                and not self.client_name.text().endswith(' '):
            self.ok_pressed = True
            qApp.exit()
        else:
            # Устанавливаем флаг видимости скрытого лейбла в True,
            # если не введено имя пользователя или введено некорректно
            self.hidden_label.setVisible(True)


if __name__ == '__main__':
    app = QApplication([])
    dialog = UsernameDialog()
    app.exec_()
