import logging

from fastapi import APIRouter, Header
from pydantic import BaseModel

from server.app.device_helper import query_online_devices, query_device_by_name
from server.app.resp import resp_error, resp_success, resp_auth_error
from server.db.database import get_db
from server.db.models import login_user, auth_user

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

session = next(get_db())


# 定义请求体的 Pydantic 模型
class LoginInfo(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(params: LoginInfo):
    logger.info(params)
    username = params.username
    password = params.password
    if len(username) == 0 or len(password) == 0:
        return resp_error('用户名或密码错误')
    if len(password) < 6:
        return resp_error('密码小于6位')
    user = login_user(session, username, password)
    if user is None:
        return resp_error("用户名或密码错误")
    logger.info(user)
    return resp_success(user.json())


@router.get("/app/devices")
def devices(auth: str = Header(...)):
    logger.info(auth)
    success, user = auth_user(session, auth)
    if success:
        device_list = []
        online_devices = query_online_devices()
        for d in user.devices:
            state = ""
            for online_d in online_devices:
                if online_d.device_name == d.device_name:
                    state = "device"
                    break
            device_list.append({"device_name": d.device_name, "state": state})
        return resp_success(device_list)
    else:
        return resp_auth_error()


@router.get("/app/device/{device_id}")
def device(device_name: str, auth: str = Header(...)):
    success, user = auth_user(session, auth)
    if success is False:
        return resp_auth_error()
    if device_name is None or len(device_name) == 0:
        return resp_error("设备不能为空")
    device_list = user.devices
    is_user_device = False
    for d in device_list:
        if device_name == d.device_name:
            is_user_device = True
    if is_user_device is False:
        return resp_error("未查询到设备")
    online_devices = query_device_by_name(device_name)
    if online_devices is None:
        return resp_error("未查询到设备")
    return resp_success(online_devices)


@router.get("/app/rebootDevice")
def reboot_device(auth: str = Header(...)):
    success, user = auth_user(session, auth)
    if success is False:
        return resp_auth_error()


@router.post("/app/editPassword")
def edit_password(params: LoginInfo, auth: str = Header(...)):
    success, user = auth_user(session, auth)
    if success is False:
        return resp_auth_error()
