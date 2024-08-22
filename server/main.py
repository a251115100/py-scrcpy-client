import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import router as api_router
from app.websocket import router as websocket_router
from server.db.database import get_db
from server.db.models import add_user

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)
app.include_router(api_router)
app.include_router(websocket_router)

if __name__ == "__main__":
    db = next(get_db())
    add_user(db, "admin", "251115100")
    uvicorn.run(app, host="0.0.0.0", port=8000)
