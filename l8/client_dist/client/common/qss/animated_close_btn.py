'''https://ru.stackoverflow.com/questions/1392351/%d0%90%d0%bd%d0%b8%d0%bc%d0%b0%d1%86%d0%b8%d1%8f-%d0%bf%d1%80%d0%b8-%d0%bd%d0%b0%d0%b2%d0%b5%d0%b4%d0%b5%d0%bd%d0%b8%d0%b8-%d0%bd%d0%b0-%d0%ba%d0%bd%d0%be%d0%bf%d0%ba%d1%83-qt-designer'''

from PyQt5 import QtCore, QtGui, QtWidgets


class AnimatedClosePushButton(QtWidgets.QPushButton):
    def __init__(self):
        super().__init__()

        self._animation = QtCore.QVariantAnimation(
            startValue=QtGui.QColor("#282c34"),
            endValue=QtGui.QColor("#1b1f25"),
            valueChanged=self._update_stylesheet,
            duration=500,
        )
        self._update_stylesheet(QtGui.QColor("#1b1f25"))

    def _update_stylesheet(self, background):
        self.setStyleSheet(
            f"""
                QPushButton {{
                    background-color: {background.name()};
                    border-radius: 6px;
                }}
            """
        )

    def enterEvent(self, event):
        self._animation.setDirection(QtCore.QAbstractAnimation.Backward)
        self._animation.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animation.setDirection(QtCore.QAbstractAnimation.Forward)
        self._animation.start()

        super().leaveEvent(event)
