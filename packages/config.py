import json
import os
from .notification import notify

config = {}


def load_config():
    if not os.path.exists("config.json"):
        notify("File Not Found", "Can't find your configuration file. Will use default configuration")
        reset()
        return

    global config
    config_file = open("config.json", "r")
    config = json.load(config_file)
    config_file.close()


def save_config():
    config_file = open("config.json", "w")
    json.dump(config, config_file)
    config_file.close()


def reset():
    config["server_address"] = "192.168.80.162"
    config["server_port"] = 9432
    config["steps"] = -2
    config["start_hotkey"] = "Ctrl+Shift+S"
    config["stop_hotkey"] = "Ctrl+Shift+P"
    config["mute_hotkey"] = "Ctrl+Shift+M"
    save_config()


load_config()
