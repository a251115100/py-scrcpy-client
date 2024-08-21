import logging

from fastapi import APIRouter, Header
from pydantic import BaseModel

from server.app.device_helper import query_online_devices, query_device_by_name
from server.app.resp import resp_error, resp_success, resp_auth_error
from server.db.database import get_db
from server.db.models import login_user, auth_user, update_user

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
        logger.info(online_devices)
        for d in user.devices:
            state = ""
            for online_d in online_devices:
                logger.info(online_d.device_name)
                if online_d.device_name == d.device_name:
                    state = "device"
            device_list.append({"device_name": d.device_name, "state": state})
        return resp_success(device_list)
    else:
        return resp_auth_error()


@router.get("/app/device")
def device(name: str, auth: str = Header(...)):
    success, user = auth_user(session, auth)
    if success is False:
        return resp_auth_error()
    if name is None or len(name) == 0:
        return resp_error("设备不能为空")
    device_list = user.devices
    is_user_device = False
    for d in device_list:
        if name == d.device_name:
            is_user_device = True
    if is_user_device is False:
        return resp_error("未查询到设备")
    online_devices = query_device_by_name(name)
    if online_devices is None:
        return resp_error("未查询到设备")
    return resp_success(online_devices)


# @router.get("/app/rebootDevice")
# def reboot_device(auth: str = Header(...)):
#     success, user = auth_user(session, auth)
#     if success is False:
#         return resp_auth_error()


@router.get("/app/editPassword")
def edit_password(password: str, auth: str = Header(...)):
    success, user = auth_user(session, auth)
    if success is False:
        return resp_auth_error()
    if len(password) == 0:
        return resp_error('密码不能为空')
    if len(password) < 6:
        return resp_error('密码小于6位')
    error, u = update_user(session, auth, password)
    if error is not None or u is None:
        return resp_error(error)
    return resp_success(u)
