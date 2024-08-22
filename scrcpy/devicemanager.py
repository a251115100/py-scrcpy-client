import time

import cv2
import numpy as np
from adbutils import adb
from fastapi import WebSocket
from starlette.websockets import WebSocketState

import scrcpy
from scrcpy import Client


def convert(frame: np.ndarray) -> bytes:
    origin_image = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
    _, b_image = cv2.imencode('.jpg', origin_image, [cv2.IMWRITE_JPEG_QUALITY, 70])
    return b_image.tobytes()


class DeviceManager:
    def __init__(
            self,
            serial: str = None,
    ):
        self.client = Client(
            device=adb.device(serial=serial),
            flip=False,
            bitrate=8000000,
            max_width=480,
            encoder_name=None,
            max_fps=20,
            block_frame=True,
            stay_awake=True
        )
        self.webSocket: WebSocket = None
        self.client.add_listener(scrcpy.EVENT_INIT, self.on_init)
        self.ratio = None
        self.width = None
        self.height = None
        self.last_send_time = 0
        self.client.on_frame = self.on_frame

    def bind_web_socket(self, web_socket: WebSocket):
        self.webSocket = web_socket

    def on_init(self):
        print(f"on_init_Serial: {self.client.device_name}")

    async def on_frame(self, frame: np.ndarray):
        if frame is None:
            return
        if self.webSocket is None:
            return
        if self.webSocket.client_state != WebSocketState.CONNECTED:
            return
        current_time_ms = int(time.time() * 1000)
        dif = current_time_ms - self.last_send_time
        if dif > 40:
            self.last_send_time = current_time_ms
        else:
            print("on_frame", dif)
            return
        await self.webSocket.send_bytes(convert(frame))

    def on_mouse_event(self, x: int, y: int, action=scrcpy.ACTION_DOWN):
        result = self.client.control.touch(x, y, action)
        # self.client.control_socket.
        # self.client.control.keycode(code, action)
        # self.client.device.click(x, y)
        print(f"on_mouse_event:{action}   result:{result}")

    def start(self):
        self.client.stop()
        self.client.start(True, True)

    def stop(self):
        self.client.stop()
