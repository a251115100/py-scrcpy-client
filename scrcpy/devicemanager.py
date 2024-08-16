import asyncio

import cv2
import numpy as np
from adbutils import adb
from fastapi import WebSocket
from starlette.websockets import WebSocketState

import scrcpy
from scrcpy import Client


def convert(frame: np.ndarray) -> bytes:
    scale_percent = 50  # 缩小到原来的50%
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    dim = (width, height)
    origin_image = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
    resized_image = cv2.resize(origin_image, dim, interpolation=cv2.INTER_AREA)
    _, b_image = cv2.imencode('.jpg', resized_image, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return b_image.tobytes()


class DeviceManager:
    def __init__(
            self,
            serial: str = None,
    ):
        self.client = Client(
            device=adb.device(serial=serial),
            flip=False,
            bitrate=100000,
            encoder_name=None,
            max_fps=40
        )
        self.webSocket: WebSocket = None
        self.max_width = 480
        self.client.add_listener(scrcpy.EVENT_INIT, self.on_init)
        self.client.add_listener(scrcpy.EVENT_FRAME, self.on_frame)
        self.ratio = None
        self.width = None
        self.height = None
        self.last_frame = None
        self.loop = asyncio.get_event_loop()

    def bind_web_socket(self, web_socket: WebSocket):
        self.webSocket = web_socket

    def on_init(self):
        print(f"on_init_Serial: {self.client.device_name}")

    async def send_bytes(self):
        if self.last_frame is None:
            return
        # print("last_frame", self.last_frame)
        await self.webSocket.send_bytes(convert(self.last_frame))
        self.last_frame = None

    def on_frame(self, frame: np.ndarray):
        if frame is None:
            return
        if self.webSocket is None:
            return
        if self.webSocket.client_state != WebSocketState.CONNECTED:
            return
        ratio = self.max_width / max(self.client.resolution)
        self.last_frame = frame
        print("on_frame")
        self.loop.run_until_complete(self.send_bytes())

    def on_mouse_event(self, x: int, y: int, action=scrcpy.ACTION_DOWN):
        self.client.control.touch(x, y, action)

    def start(self):
        self.client.stop()
        self.client.start(True, True)
