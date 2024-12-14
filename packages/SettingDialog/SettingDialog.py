from .UI_SettingDialog import Ui_SettingDialog
from PyQt6.QtWidgets import QDialog
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator, QKeySequence
from PyQt6.QtCore import QRegularExpression
from packages.config import config, save_config


class SettingDialog(QDialog, Ui_SettingDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Add IPv4 validator to server address field
        ip_range = r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
        # Adjust the regular expression to make the entire IP address pattern optional
        ip_regex = QRegularExpression(f"^(?:{ip_range}\.{ip_range}\.{ip_range}\.{ip_range})?$")
        ipv4_validator = QRegularExpressionValidator(ip_regex)
        self.serverAddressLineEdit.setValidator(ipv4_validator)

        # Add Integer validator to server port field
        port_validator = QIntValidator()
        self.serverPortLineEdit.setValidator(port_validator)

        # Initialize values
        self.serverAddressLineEdit.setText(config["server_address"])
        self.serverPortLineEdit.setText(str(config["server_port"]))
        self.pitchLevelSlider.setValue(config["steps"])
        self.pitchLevelLabel.setText(f"Pitch Level: {config['steps']}")
        self.startHotkeySequenceEdit.setKeySequence(QKeySequence(config["start_hotkey"]))
        self.stopHotkeySequenceEdit.setKeySequence(QKeySequence(config["stop_hotkey"]))
        self.muteHotkeySequenceEdit.setKeySequence(QKeySequence(config["mute_hotkey"]))
        self.resetButton.clicked.connect(self.reset)
        self.pitchLevelSlider.valueChanged.connect(self.pitch_level_changed)

    def save(self):
        config["server_address"] = self.serverAddressLineEdit.text()
        config["server_port"] = int(self.serverPortLineEdit.text())
        config["steps"] = self.pitchLevelSlider.value()
        config["start_hotkey"] = self.startHotkeySequenceEdit.keySequence().toString()
        config["stop_hotkey"] = self.stopHotkeySequenceEdit.keySequence().toString()
        config["mute_hotkey"] = self.muteHotkeySequenceEdit.keySequence().toString()
        save_config()

    def reset(self):
        self.serverAddressLineEdit.setText("192.168.80.162")
        self.serverPortLineEdit.setText("9432")
        self.pitchLevelSlider.setValue(-2)
        self.startHotkeySequenceEdit.setKeySequence(QKeySequence("Ctrl+Shift+S"))
        self.stopHotkeySequenceEdit.setKeySequence(QKeySequence("Ctrl+Shift+P"))
        self.muteHotkeySequenceEdit.setKeySequence(QKeySequence("Ctrl+Shift+M"))

    def pitch_level_changed(self, value: int):
        self.pitchLevelLabel.setText(f"Pitch Level: {value}")
