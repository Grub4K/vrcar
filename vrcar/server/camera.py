from __future__ import annotations

import io
import logging
import multiprocessing
import socket

import picamera2
import picamera2.encoders
import picamera2.outputs

logger = logging.getLogger(__name__)


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame: bytes | None = None
        self.condition = multiprocessing.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
        return len(buf)


def run(address: tuple[str, int]):
    logger.info("Starting...")
    stream = StreamingOutput()
    picam2 = picamera2.Picamera2()
    encoder = picamera2.encoders.MJPEGEncoder()
    output = picamera2.outputs.FileOutput(stream)

    picam2.configure(
        picam2.create_video_configuration(
            main={"size": (1024, 768)},
            buffer_count=2,
        )
    )

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.info("Awaiting connection")
    server.bind(address)
    server.listen()

    client, incoming_address = server.accept()
    logger.info(f"Accepted connection from {incoming_address[0]}:{incoming_address[1]}")
    picam2.start_recording(encoder, output)

    while True:
        with stream.condition:
            stream.condition.wait()
            frame = stream.frame

        if frame:
            length = len(frame).to_bytes(4, "big")
            client.send(length)
            client.send(frame)
