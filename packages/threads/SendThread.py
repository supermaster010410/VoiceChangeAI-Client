import socket
from threading import Event, Thread
from pyaudio import Stream
from logging import Logger
import errno
from packages import notify


class SendThread(Thread):
    def __init__(self, client_socket: socket.socket, input_stream: Stream, chunk: int, logger: Logger, stop):
        self._client_socket = client_socket
        self._input_stream = input_stream
        self._chunk = chunk
        self._logger = logger
        self._stop = Event()
        self._stop_method = stop
        super().__init__()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()

    def run(self):
        print("Start sending process")
        self._logger.info("Start sending process")
        while True:
            if self.stopped():
                break
            try:
                data = self._input_stream.read(self._chunk)
                self._client_socket.sendall(data)
            except socket.error as error:
                if error.errno == errno.WSAECONNRESET:
                    print(str(error))
                    self._logger.error(str(error))
                    notify(f"Error {error.errno}", error.strerror)
                    self._stop_method()
                    break
            except Exception as error:
                print(str(error))
                self._logger.error(str(error))
                self._stop_method()
                break
        print("Stop sending process")
        self._logger.info("Stop sending process")
