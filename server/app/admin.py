from fastapi import APIRouter

router = APIRouter()


@router.get("/admin/users")
def users():
    return {"message": "Items list"}


@router.get("/admin/createUser")
def create_user(item_id: int):
    return {"item_id": item_id}


@router.get("/admin/asyncDevices")
def async_devices(item_id: int):
    return {"item_id": item_id}


@router.get("/admin/devices")
def devices(item_id: int):
    return {"item_id": item_id}


@router.get("/admin/bindDevice")
def bind_device(item_id: int):
    return {"item_id": item_id}


@router.get("/admin/unbindDevice")
def unbind_device(item_id: int):
    return {"item_id": item_id}


@router.get("/admin/deleteDevice")
def delete_device(item_id: int):
    return {"item_id": item_id}


@router.get("/admin/deleteUser")
def delete_user(item_id: int):
    return {"item_id": item_id}
