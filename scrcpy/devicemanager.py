import asyncio
import time

import cv2
import nest_asyncio
import numpy as np
from adbutils import adb
from fastapi import WebSocket
from starlette.websockets import WebSocketState

import scrcpy
from scrcpy import Client

nest_asyncio.apply()


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
            encoder_name=None,
            max_fps=20,
            block_frame=True,
            stay_awake=True
        )
        self.webSocket: WebSocket = None
        self.max_width = 480
        self.client.add_listener(scrcpy.EVENT_INIT, self.on_init)
        self.client.add_listener(scrcpy.EVENT_FRAME, self.on_frame)
        self.ratio = None
        self.width = None
        self.height = None
        self.last_frame = None
        self.loop = asyncio.new_event_loop()
        self.last_send_time = 0
        # self.task = asyncio.create_task(self.send_bytes())

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
        self.last_frame = frame
        current_time_ms = int(time.time() * 1000)
        dif = current_time_ms - self.last_send_time
        if dif > 40:
            self.last_send_time = current_time_ms
        else:
            print("on_frame", dif)
            return
        # print("on_frame")
        try:
            self.loop.run_until_complete(self.send_bytes())
        except Exception:
            print(Exception)
            self.last_frame = None

    def on_mouse_event(self, x: int, y: int, action=scrcpy.ACTION_DOWN):
        self.client.control.touch(x, y, action)

    def key_event(self, action: str):
        self.client.device.keyevent(action)

    # def on_back(self):
    #     self.client.device.keyevent("BACK")
    #
    # def on_home(self):
    #     self.client.device.keyevent("HOME")
    #
    # def app_switch(self):
    #     self.client.device.keyevent("APP_SWITCH")
    #
    # def on_reboot(self):
    #     self.client.device.keyevent("HOME")

    def start(self):
        self.client.stop()
        self.client.start(True, True)

    def stop(self):
        self.client.stop()
