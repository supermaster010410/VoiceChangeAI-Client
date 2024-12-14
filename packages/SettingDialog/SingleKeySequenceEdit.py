from PyQt6.QtWidgets import QKeySequenceEdit
from PyQt6.QtGui import QKeyEvent, QKeySequence


class SingleKeySequenceEdit(QKeySequenceEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event: QKeyEvent):
        # Create a QKeySequence from the key event, but only use the first key combination
        key_sequence = QKeySequence(event.keyCombination())

        # Set the key sequence to the widget, replacing any previous input
        self.setKeySequence(key_sequence)

        # Accept the event to prevent further processing
        event.accept()
