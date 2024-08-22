from adbutils import adb
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import scrcpy
from scrcpy import DeviceManager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("id", websocket.query_params.get("id"))
    devices = adb.device_list()
    print("serial", devices[0].serial)
    device_manager = DeviceManager(serial=devices[0].serial)
    device_manager.start()
    device_manager.bind_web_socket(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            x = data["x"]
            y = data["y"]
            action_type = data["type"]
            print(data)
            action = None
            if action_type == "ACTION_DOWN":
                action = scrcpy.ACTION_DOWN
            if action_type == "ACTION_MOVE":
                action = scrcpy.ACTION_MOVE
            if action_type == "ACTION_UP":
                action = scrcpy.ACTION_UP
            if action is not None:
                device_manager.on_mouse_event(x, y, action)
    except WebSocketDisconnect:
        device_manager.stop()
        # 处理连接断开
