import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout, QMainWindow, QVBoxLayout

sys.path.append('../')
from common.qss import style
from client.add_menu_corners_radius import AddMenuCornersRadius
from common.variables import HEIGHT, WIDTH


class Ui_MainClientWindow(QMainWindow):
    def __init__(self, width_main_window=WIDTH, height_main_window=HEIGHT):
        super().__init__()
        self.corner_radius = None
        self.central_widget = None
        self.menu_bar = None
        self.menu = None
        self.menu_2 = None
        self.menu_add_contact = None
        self.menu_del_contact = None
        self.menu_exit = None
        self.clear_btn = None
        self.send_btn = None
        self.add_contact_btn = None
        self.remove_contact_btn = None
        self.contacts_label = None
        self.history_label = None
        self.new_message_label = None
        self.contacts_list = None
        self.messages_list = None
        self.message_text = None

        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.width = self.screenRect.width()
        self.height = self.screenRect.height()

        self.width_main_window = width_main_window
        self.height_main_window = height_main_window

    def setupUi(self, MainClientWindow):
        MainClientWindow.setObjectName("MainClientWindow")
        MainClientWindow.setBaseSize(QtCore.QSize(self.width_main_window, self.height_main_window))
        MainClientWindow.move(
            self.width // 2 - self.width_main_window // 2,
            self.height // 2 - self.height_main_window // 2,
        )

        self.central_widget = QtWidgets.QWidget(MainClientWindow)
        self.central_widget.setObjectName("central_widget")
        self.central_widget.setStyleSheet(style.COMMON_THEME)
        self.central_widget.setMinimumSize(self.width_main_window, self.height_main_window)

        self.messages_list = QtWidgets.QListView(self.central_widget)
        self.messages_list.setStyleSheet(style.MESSAGES_HIST_THEME)
        self.messages_list.setGeometry(QtCore.QRect(220, 10, 570, 575))
        self.messages_list.setObjectName('messages_list')

        self.message_text = QtWidgets.QTextEdit(self.central_widget)
        self.message_text.setStyleSheet(style.MESSAGE_THEME)
        self.message_text.setPlaceholderText('Write a message...')
        self.message_text.setGeometry(QtCore.QRect(220, 535, 570, 50))
        self.message_text.setObjectName("message_text")

        self.send_btn = QtWidgets.QPushButton(self.central_widget)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setShortcut(Qt.Key_Return)
        self.send_btn.setToolTip('Send a message')
        self.send_btn.setIcon(QIcon('common/img/msg_send.png'))
        self.send_btn.setIconSize(QSize(49, 49))
        self.send_btn.setStyleSheet(style.NONE_BORDER_BGCOLOR_BTN_THEME)
        self.send_btn.setGeometry(QtCore.QRect(735, 535, 50, 50))
        self.send_btn.setObjectName('send_btn')

        self.clear_btn = QtWidgets.QPushButton(self.central_widget)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setToolTip('Clear message field')
        self.clear_btn.setIcon(QIcon('common/img/msg_clear.png'))
        self.clear_btn.setIconSize(QSize(20, 20))
        self.clear_btn.setStyleSheet(style.NONE_BORDER_BGCOLOR_BTN_THEME)
        self.clear_btn.setGeometry(QtCore.QRect(697, 545, 31, 31))
        self.clear_btn.setObjectName('clear_btn')

        self.contacts_list = QtWidgets.QListView(self.central_widget)
        self.contacts_list.setStyleSheet(style.CONTACTS_THEME)
        self.contacts_list.setGeometry(QtCore.QRect(10, 10, 200, 575))
        self.contacts_list.setObjectName('contacts_list')

        self.add_contact_btn = QtWidgets.QPushButton(self.central_widget)
        self.add_contact_btn.setCursor(Qt.PointingHandCursor)
        self.add_contact_btn.setToolTip('Add a contact')
        self.add_contact_btn.setIcon(QIcon('common/img/user_add.png'))
        self.add_contact_btn.setIconSize(QSize(25, 25))
        self.add_contact_btn.setStyleSheet(style.NONE_BORDER_BGCOLOR_BTN_THEME)
        self.add_contact_btn.setGeometry(QtCore.QRect(13, 552, 30, 30))
        self.add_contact_btn.setObjectName('add_contact_btn')

        self.remove_contact_btn = QtWidgets.QPushButton(self.central_widget)
        self.remove_contact_btn.setCursor(Qt.PointingHandCursor)
        self.remove_contact_btn.setToolTip('Delete a contact')
        self.remove_contact_btn.setIcon(QIcon('common/img/user_remove.png'))
        self.remove_contact_btn.setIconSize(QSize(25, 25))
        self.remove_contact_btn.setStyleSheet(style.NONE_BORDER_BGCOLOR_BTN_THEME)
        self.remove_contact_btn.setGeometry(QtCore.QRect(177, 552, 30, 30))
        self.remove_contact_btn.setObjectName('remove_contact_btn')

        self.new_message_label = QtWidgets.QLabel(self.central_widget)
        self.new_message_label.setStyleSheet(style.NEW_MESSAGE_LABEL_THEME)
        self.new_message_label.setAlignment(Qt.AlignCenter)
        self.new_message_label.setGeometry(QtCore.QRect(
            self.width_main_window - self.messages_list.width() // 2 - self.new_message_label.width() - 10,
            self.height_main_window - self.messages_list.height() // 2 - self.new_message_label.height() - 10,
            220,
            30
        ))


        MainClientWindow.setCentralWidget(self.central_widget)
        self.menu_bar = QtWidgets.QMenuBar(MainClientWindow)
        self.menu_bar.setStyleSheet(style.MENU_BAR_THEME)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, self.width_main_window, 24))
        self.menu_bar.setObjectName('menu_bar')

        self.menu = AddMenuCornersRadius(self.menu_bar)
        self.menu.setObjectName('menu')
        self.menu_2 = AddMenuCornersRadius(self.menu_bar)
        self.menu_2.setObjectName('menu_2')

        MainClientWindow.setMenuBar(self.menu_bar)
        self.menu_exit = QtWidgets.QAction(MainClientWindow)
        self.menu_exit.setObjectName('menu_exit')

        self.menu_add_contact = QtWidgets.QAction(MainClientWindow)
        self.menu_add_contact.setObjectName("menu_add_contact")

        self.menu_del_contact = QtWidgets.QAction(MainClientWindow)
        self.menu_del_contact.setObjectName('menu_del_contact')

        self.menu.addAction(self.menu_exit)

        self.menu_2.addAction(self.menu_add_contact)
        self.menu_2.addAction(self.menu_del_contact)
        self.menu_2.addSeparator()

        self.menu_bar.addAction(self.menu.menuAction())
        self.menu_bar.addAction(self.menu_2.menuAction())

        self.retranslateUi(MainClientWindow)
        self.clear_btn.clicked.connect(self.message_text.clear)
        QtCore.QMetaObject.connectSlotsByName(MainClientWindow)

    def retranslateUi(self, MainClientWindow):
        _translate = QtCore.QCoreApplication.translate
        MainClientWindow.setWindowTitle(_translate("MainClientWindow", "Telegram на минималках"))
        # self.send_btn.setText(_translate("MainClientWindow", ">>"))
        # self.clear_btn.setText(_translate("MainClientWindow", "<-"))
        # self.add_contact_btn.setText(_translate("MainClientWindow", "Добавить контакт"))
        # self.remove_contact_btn.setText(_translate("MainClientWindow", "Удалить контакт"))
        # self.contacts_label.setText(_translate("MainClientWindow", "Contacts:"))
        # self.history_label.setText(_translate("MainClientWindow", "Messages:"))
        self.menu.setTitle(_translate("MainClientWindow", "File"))
        self.menu_2.setTitle(_translate("MainClientWindow", "Contacts"))
        self.menu_exit.setText(_translate("MainClientWindow", "Exit"))
        self.menu_add_contact.setText(_translate("MainClientWindow", "Invite"))
        self.menu_del_contact.setText(_translate("MainClientWindow", "Delete"))
