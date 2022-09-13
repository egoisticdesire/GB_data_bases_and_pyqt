from PyQt5 import QtCore, QtGui, QtWidgets


class AddMenuCornersRadius(QtWidgets.QMenu):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.radius = 6
        self.setStyleSheet(f'''
            QMenu {{
                margin: 2px;
                background-color: rgb(40,44,52);
                color: rgb(171,178,191);
                padding: 1px 50px 1px 1px;
            }}
            QMenu::item {{
                padding: 1px 50px 1px 5px;
                border-radius: {self.radius}px;
            }}
            QMenu::item:selected {{
                background-color: rgb(27,31,37);
            }}
            QMenu::item:pressed {{
                background-color: rgb(53,115,212);
                color: rgb(27,31,37);
            }}
        ''')

    def resizeEvent(self, event):
        path = QtGui.QPainterPath()
        rect = QtCore.QRectF(self.rect()).adjusted(.5, .5, -1.5, -1.5)
        path.addRoundedRect(rect, self.radius, self.radius)
        region = QtGui.QRegion(path.toFillPolygon(QtGui.QTransform()).toPolygon())
        self.setMask(region)
