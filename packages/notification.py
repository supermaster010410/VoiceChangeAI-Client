from win10toast import ToastNotifier
from PyQt6.QtWidgets import QMessageBox

toast = ToastNotifier()


def notify(title: str, message: str):
    toast.show_toast(
        title,
        message,
        duration=1,
        icon_path="resource/off.png",
        threaded=True,
    )


def show_messagebox(message: str):
    messagebox = QMessageBox()
    messagebox.critical(None, "Error", message)
