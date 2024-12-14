from .UI_StatusDialog import Ui_StatusDialog
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import Qt


class StatusDialog(QDialog, Ui_StatusDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.closeButton.clicked.connect(self.handle_close)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setMouseTracking(True)
        self.pressed = False
        self.offset = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.pressed = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.pressed:
            self.move(self.pos() + event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.pressed = False

    def handle_close(self):
        self.hide()
