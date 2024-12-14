"""
Client Program - route audio data from microphone to server and play the audio from server
"""
import errno
import socket
import sys
import pyaudio
import keyboard
import win32event
import win32api
import winerror
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from packages.threads import SendThread, ReceiveThread, StreamThread
from packages.SettingDialog import SettingDialog
from packages.StatusDialog import StatusDialog
from packages import config, logger, notify, show_messagebox

BUFFER_SIZE = 40960
CHUNK = 5120
SAMPLE_RATE = 44100


def start():
    """
    Start audio processing
    """
    global send_thread, receive_thread, client_socket, server_address
    try:
        if mute_action.isChecked():
            return
        # send start message
        server_address = (config["server_address"], config["server_port"])
        tray.setIcon(QIcon("resource/loading.svg"))
        status_dlg.muteButton.setIcon(QIcon("resource/loading.svg"))
        status_dlg.muteButton.setDisabled(True)
        status_dlg.conversionButton.setDisabled(True)
        tray.setToolTip("Connecting to server...")

        # connect to server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
        client_socket.connect(server_address)
        print("connected to server:", server_address)
        logger.info("connected to server: %s", str(server_address))

        # send steps for pitch conversion
        steps = int(config["steps"]).to_bytes(1, "little", signed=True)
        client_socket.sendall(steps)

        # stop streaming
        stream_thread.stop()

        # start sending voice
        send_thread = SendThread(client_socket, input_stream, CHUNK, logger, stop)
        send_thread.start()

        # start receiving converted voice
        receive_thread = ReceiveThread(client_socket, output_stream, BUFFER_SIZE, logger)
        receive_thread.start()

        # change menu status
        start_action.setDisabled(True)
        stop_action.setEnabled(True)
        status_dlg.conversionButton.setEnabled(True)
        status_dlg.muteButton.setEnabled(True)
        status_dlg.conversionButton.setChecked(True)
        status_dlg.closeButton.setDisabled(False)
        tray.setIcon(QIcon("resource/on.png"))
        status_dlg.muteButton.setIcon(QIcon("resource/on.png"))

        notify("Success", "Connected to server successfully and start pitch conversion.")
        tray.setToolTip("Pitch Conversion: ON")
    except socket.error as error:
        print(str(error))
        logger.error(str(error))
        status_dlg.muteButton.setEnabled(True)
        status_dlg.conversionButton.setEnabled(True)
        status_dlg.conversionButton.setChecked(False)
        status_dlg.muteButton.setIcon(QIcon("resource/off.png"))
        tray.setIcon(QIcon("resource/off.png"))
        tray.setToolTip("Pitch Conversion: OFF")
        if error.errno == errno.WSAECONNREFUSED or error.errno == errno.WSAETIMEDOUT:
            notify(f"Error {error.errno}", error.strerror)

    except Exception as error:
        print(str(error))
        status_dlg.muteButton.setEnabled(True)
        status_dlg.conversionButton.setEnabled(True)
        status_dlg.conversionButton.setChecked(False)
        status_dlg.muteButton.setIcon(QIcon("resource/off.png"))
        tray.setIcon(QIcon("resource/off.png"))
        tray.setToolTip("Pitch Conversion: OFF")
        logger.error(str(error))


def stop():
    """
    Stop audio processing
    """
    try:
        if mute_action.isChecked():
            return

        # close connection
        client_socket.close()
        print("Close connection between server:", server_address)
        logger.info("Close connection between server: %s", str(server_address))

        # start streaming
        global stream_thread
        stream_thread = StreamThread(input_stream, output_stream, CHUNK, logger)
        stream_thread.start()

        # stop sending and receiving
        send_thread.stop()
        receive_thread.stop()

        # change menu status
        start_action.setEnabled(True)
        stop_action.setDisabled(True)
        status_dlg.conversionButton.setChecked(False)
        tray.setIcon(QIcon("resource/off.png"))
        status_dlg.muteButton.setIcon(QIcon("resource/off.png"))

        notify("Alert", "Pitch conversion is stopped.")
        tray.setToolTip("Pitch Conversion: OFF")
    except Exception as error:
        print("stop", "-", str(error))
        logger.error("stop - " + str(error))


def mute():
    """
    mute voice
    """
    global send_thread, receive_thread, stream_thread, is_mute
    try:
        if stop_action.isEnabled() and not is_mute:  # mute when voice converting is on
            send_thread.stop()
            receive_thread.stop()
            mute_action.setChecked(True)
            status_dlg.muteButton.setChecked(True)
            tray.setIcon(QIcon("resource/on-mute.png"))
            status_dlg.muteButton.setIcon(QIcon("resource/on-mute.png"))

        elif stop_action.isEnabled() and is_mute:  # unmute when voice converting in on
            send_thread = SendThread(client_socket, input_stream, CHUNK, logger, stop)
            send_thread.start()
            receive_thread = ReceiveThread(client_socket, output_stream, BUFFER_SIZE, logger)
            receive_thread.start()
            mute_action.setChecked(False)
            status_dlg.muteButton.setChecked(False)
            tray.setIcon(QIcon("resource/on.png"))
            status_dlg.muteButton.setIcon(QIcon("resource/on.png"))

        elif start_action.isEnabled() and not is_mute:  # mute when voice converting is off
            stream_thread.stop()
            mute_action.setChecked(True)
            status_dlg.muteButton.setChecked(True)
            tray.setIcon(QIcon("resource/off-mute.png"))
            status_dlg.muteButton.setIcon(QIcon("resource/off-mute.png"))

        elif start_action.isEnabled() and is_mute:  # unmute when voice converting is off
            stream_thread = StreamThread(input_stream, output_stream, CHUNK, logger)
            stream_thread.start()
            mute_action.setChecked(False)
            status_dlg.muteButton.setChecked(False)
            tray.setIcon(QIcon("resource/off.png"))
            status_dlg.muteButton.setIcon(QIcon("resource/off.png"))

        is_mute = not is_mute

    except Exception as error:
        print(str(error))
        logger.error(str(error))


def quit_app():
    """
    Quit app
    """
    # close connection
    client_socket.close()
    print("Close connection between server:", server_address)
    logger.info("Close connection between server: %s", str(server_address))

    # stop all audio processing
    send_thread.stop()
    receive_thread.stop()
    stream_thread.stop()

    # close streaming
    input_stream.close()
    output_stream.close()

    # close app
    app.quit()


def show_setting():
    global start_hotkey, stop_hotkey, mute_hotkey
    dlg = SettingDialog()
    ret = dlg.exec()
    if ret == 1:
        dlg.save()
        keyboard.remove_hotkey(start_hotkey)
        keyboard.remove_hotkey(stop_hotkey)
        keyboard.remove_hotkey(mute_hotkey)
        start_hotkey = keyboard.add_hotkey(config["start_hotkey"], start)
        stop_hotkey = keyboard.add_hotkey(config["stop_hotkey"], stop)
        mute_hotkey = keyboard.add_hotkey(config["mute_hotkey"], mute)


def start_stop_pitch_conversion():
    if status_dlg.conversionButton.isEnabled():
        if status_dlg.conversionButton.isChecked():
            start()
        else:
            stop()


# Create an application
app = QApplication([])
app.setQuitOnLastWindowClosed(False)

# Check program is already running or not.
mutex_name = "voice-change-ai-client-{D0E858DF-985E-4907-B7FB-8D732C3FC3B9}"
mutex = win32event.CreateMutex(None, False, mutex_name)

if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    show_messagebox("Program is already running.")
    sys.exit(1)

try:
    # find the input and output deviceW
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get("deviceCount")

    output_device_index = None
    for i in range(0, num_devices):
        if p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels') > 0 and \
                p.get_device_info_by_host_api_device_index(0, i).get('name').startswith("Line 1"):
            output_device_index = i

    if output_device_index is None:
        show_messagebox("Can't find Virtual Audio Cable devices. Please install Virtual Audio Cable.")
        sys.exit(1)
    input_device_index = p.get_default_input_device_info().get("index")

    logger.info(p.get_default_input_device_info())

    for i in range(0, num_devices):
        logger.info(p.get_device_info_by_host_api_device_index(0, i))
        if p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels') > 0 and \
                p.get_device_info_by_host_api_device_index(0, i).get('name').startswith("Line 1") and \
                i == p.get_default_output_device_info().get("index"):
            show_messagebox("Default output device shouldn't be Virtual Audio Cable. Change to normal speaker.")
            sys.exit(1)
        if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0 and \
                p.get_device_info_by_host_api_device_index(0, i).get('name').startswith("Line 1") and \
                i == p.get_default_input_device_info().get("index"):
            show_messagebox("Default input device shouldn't be Virtual Audio Cable. Change to normal microphone.")
            sys.exit(1)

    # create input, output audio stream
    input_stream = p.open(
        format=pyaudio.paFloat32,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=input_device_index,
        frames_per_buffer=CHUNK,
    )
    output_stream = p.open(
        format=pyaudio.paFloat32,
        channels=1,
        rate=SAMPLE_RATE,
        output=True,
        output_device_index=output_device_index,
        frames_per_buffer=CHUNK,
    )

    # send start message
    server_address = (config["server_address"], config["server_port"])

    # create threads
    client_socket = socket.socket()
    send_thread = SendThread(client_socket, input_stream, CHUNK, logger, stop)
    receive_thread = ReceiveThread(client_socket, output_stream, CHUNK, logger)

    # start stream thread
    stream_thread = StreamThread(input_stream, output_stream, CHUNK, logger)
    stream_thread.start()

except Exception as e:
    print(str(e))
    logger.error(str(e))
    sys.exit(1)


# Create an icon
icon = QIcon("resource/off.png")

status_dlg = StatusDialog()
status_dlg.show()
status_dlg.muteButton.setCheckable(True)
status_dlg.conversionButton.setChecked(False)

# Create the tray
tray = QSystemTrayIcon()
tray.setIcon(icon)
status_dlg.muteButton.setIcon(icon)
tray.setVisible(True)

# Create the menu
menu = QMenu()
quit_action = QAction("Quit")
quit_action.triggered.connect(quit_app)
menu.addAction(quit_action)

start_action = QAction("Start")
start_action.triggered.connect(start)
menu.addAction(start_action)

stop_action = QAction("Stop")
stop_action.triggered.connect(stop)
stop_action.setDisabled(True)
menu.addAction(stop_action)

mute_action = QAction("Mute")
mute_action.triggered.connect(mute)
mute_action.setCheckable(True)
menu.addAction(mute_action)

setting_action = QAction("Settings")
setting_action.triggered.connect(show_setting)
menu.addAction(setting_action)

widget_action = QAction("Show Widget")
widget_action.triggered.connect(status_dlg.show)
menu.addAction(widget_action)

status_dlg.conversionButton.clicked.connect(start_stop_pitch_conversion)
status_dlg.muteButton.clicked.connect(mute)

is_mute = False

# Add the menu to the tray
tray.setContextMenu(menu)
tray.setToolTip("Pitch Conversion: OFF")

# add mute/unmute hotkey
start_hotkey = keyboard.add_hotkey(config["start_hotkey"], start)
stop_hotkey = keyboard.add_hotkey(config["stop_hotkey"], stop)
mute_hotkey = keyboard.add_hotkey(config["mute_hotkey"], mute)

# Run application
app.exec()
