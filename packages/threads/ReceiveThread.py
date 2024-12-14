from socket import socket
from threading import Thread, Event
from pyaudio import Stream
from logging import Logger


class ReceiveThread(Thread):
    def __init__(self, client_socket: socket, output_stream: Stream, buffer_size: int, logger: Logger):
        self._client_socket = client_socket
        self._output_stream = output_stream
        self._buffer_size = buffer_size
        self._logger = logger
        self._stop = Event()
        super().__init__()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()

    def run(self):
        print("Start receiving process")
        self._logger.info("Start receiving process")
        while True:
            if self.stopped():
                break
            try:
                data = self._client_socket.recv(self._buffer_size)
                self._output_stream.write(data)
            except Exception as error:
                print(str(error))
                self._logger.error(str(error))
                break
        print("Stop receiving process")
        self._logger.info("Stop receiving process")
