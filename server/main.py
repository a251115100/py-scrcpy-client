import uvicorn
from fastapi import FastAPI

from app import router as api_router
from app.websocket import router as websocket_router
from db.database import get_db
from db.models import add_user

app = FastAPI()
app.include_router(api_router)
app.include_router(websocket_router)

if __name__ == "__main__":
    db = next(get_db())
    add_user(db, "admin", "251115100")
    uvicorn.run(app, host="0.0.0.0", port=8011)
