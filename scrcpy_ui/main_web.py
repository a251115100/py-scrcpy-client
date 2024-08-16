from typing import Set

import uvicorn
from adbutils import adb
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import scrcpy
from scrcpy import DeviceManager

app = FastAPI()

# 跟踪所有活动的 WebSocket 连接
active_connections: Set[WebSocket] = set()

devices = adb.device_list()
print("serial", devices[0].serial)
device_manager = DeviceManager(serial=devices[0].serial)

# print("device.prop", device.prop)

# HTML 页面，用于测试 WebSocket 客户端
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>WebSocket Test</h1>
        <textarea id="messageInput" placeholder="Type a message..."></textarea>
        <img src="path/to/image.jpg" id="img" width="768" height="1280">
        <button onclick="sendMessage()">Send</button>
        <div id="messages"></div>
        <script>
            var ws = new WebSocket("ws://localhost:8011/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('img');
                console.log(event.data);
                const reader = new FileReader();

reader.onload = function(e) {
    const dataURL = e.target.result;
    const img = document.getElementById('img');
    img.src = dataURL;
};

// 将 Blob 对象读取为 Data URL
reader.readAsDataURL(event.data);
                
            };
            function sendMessage() {
                var input = document.getElementById("messageInput");
                ws.send(input.value);
                input.value = '';
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    device_manager.start()
    device_manager.bind_web_socket(websocket)
    print(websocket.query_params.get("id"))
    active_connections.add(websocket)
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
            # 广播消息到所有连接
            # for connection in active_connections:
            #     if connection != websocket:  # 不向发送消息的连接回复
            #         await connection.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        # 处理连接断开
        active_connections.remove(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011)
