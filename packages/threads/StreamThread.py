from threading import Thread, Event
from pyaudio import Stream
from logging import Logger


class StreamThread(Thread):
    def __init__(self, input_stream: Stream, output_stream: Stream, chunk: int, logger: Logger):
        self._input_stream = input_stream
        self._output_stream = output_stream
        self._chunk = chunk
        self._logger = logger
        self._stop = Event()
        super().__init__()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()

    def run(self):
        print("Start streaming process")
        self._logger.info("Start streaming process")
        while True:
            if self.stopped():
                break
            try:
                data = self._input_stream.read(self._chunk)
                self._output_stream.write(data)
            except Exception as error:
                print(str(error))
                self._logger.error(str(error))
                break
        print("Stop streaming process")
        self._logger.info("Stop streaming process")
