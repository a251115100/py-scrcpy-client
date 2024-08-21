from adbutils import adb
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import scrcpy
from scrcpy import DeviceManager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    serial = websocket.query_params.get("id")
    devices = adb.device_list()
    has_device = False
    for d in devices:
        if d.serial == serial:
            has_device = True
    if has_device is False:
        await websocket.close(code=404, reason="设备未在线")
        return
    print("serial", serial)
    device_manager = DeviceManager(serial=serial)
    device_manager.start()
    device_manager.bind_web_socket(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            x = data["x"]
            y = data["y"]
            action_type = data.get("type")
            print(data)
            action = None
            if action_type == "ACTION_DOWN":
                action = scrcpy.ACTION_DOWN
            if action_type == "ACTION_MOVE":
                action = scrcpy.ACTION_MOVE
            if action_type == "ACTION_UP":
                action = scrcpy.ACTION_UP
            if action:
                device_manager.on_mouse_event(x, y, action)
    except WebSocketDisconnect:
        device_manager.stop()
        # 处理连接断开
