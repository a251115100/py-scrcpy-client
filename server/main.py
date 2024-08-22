import logging
import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from server.app import router as api_router
from server.app.websocket import router as websocket_router
from server.db.database import get_db
from server.db.models import add_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)
current_directory = os.getcwd()
index_path = os.path.join(f"{current_directory}/static/", "index.html")
app.include_router(api_router)
app.include_router(websocket_router)
app.mount("/static", StaticFiles(directory=f"{current_directory}/static/"), name="static")


@app.get("/")
async def serve_index():
    logging.info(f"serve_index: {index_path}")
    return FileResponse(index_path)


if __name__ == "__main__":
    current_directory = os.getcwd()
    logging.info(f"当前工作目录是: {current_directory}")
    db = next(get_db())
    add_user(db, "admin", "251115100")
    uvicorn.run(app, host="0.0.0.0", port=8000)
