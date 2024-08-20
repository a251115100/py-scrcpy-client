from adbutils import adb
from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
def login():
    return {"message": "Items list"}


@router.get("/app/devices")
def devices():
    list = adb.device_list()
    list[0].name = list[0].prop.name
    print("devices", list)
    return {"devices": list}


@router.get("/app/device")
def device(item_id: int):
    return {"item_id": item_id}


@router.get("/app/rebootDevice")
def reboot_device(item_id: int):
    return {"item_id": item_id}


@router.post("/app/editPassword")
def edit_password(item_id: int):
    return {"item_id": item_id}
