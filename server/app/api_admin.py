import logging

from fastapi import APIRouter, Header

from server.app.device_helper import query_online_devices
from server.app.resp import resp_error, resp_auth_error, resp_success
from server.db.database import get_db
from server.db.models import auth_admin, get_users, add_user, delete_user, get_user, delete_device, bind_device, \
    unbind_device

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()
session = next(get_db())


@router.get("/admin/users")
def users(auth: str = Header(...)):
    user = auth_admin(session, auth)
    if user is None:
        return resp_auth_error()
    if user.is_admin() is False:
        return resp_error("没有权限", code=-98)
    user_list = get_users(session)
    return resp_success(user_list)


@router.get("/admin/createUser")
def create_user(username: str, password: str, auth: str = Header(...)):
    user = auth_admin(session, auth)
    if user is None:
        return resp_auth_error()
    if user.is_admin() is False:
        return resp_error("没有权限", code=-98)
    if len(username) == 0:
        return resp_error("用户名不能为空")
    if len(password) == 0:
        return resp_error("密码不能为空")
    if len(password) < 6:
        return resp_error("密码不能小于6位")
    msg, user = add_user(session, username, password)
    if msg is not None:
        return resp_error(msg)
    return resp_success(user.simple_user())


@router.get("/admin/asyncDevices")
def async_devices(user_id: int, auth: str = Header(...)):
    user = auth_admin(session, auth)
    if user is None:
        return resp_auth_error()
    if user.is_admin() is False:
        return resp_error("没有权限", code=-98)
    online_devices = query_online_devices()
    u = get_user(session, user_id)
    if u is None:
        return resp_error("系统异常,请稍后再试")
    result = {}
    for od in online_devices:
        result[od.device_name] = {"bind": False, "online": True}
    for d in u.devices:
        device_info = result.get(d.device_name)
        if device_info is None:
            result[d.device_name] = {"bind": False, "online": False}
        else:
            result[d.device_name]["bind"] = True
    all_list = []
    for k in result.keys():
        v = result[k]
        all_list.append({"name": k, "bind": v["bind"], "online": v["online"]})
    return resp_success(all_list)


@router.get("/admin/bindDevice")
def api_bind_device(user_id: int, name: str, auth: str = Header(...)):
    user = auth_admin(session, auth)
    if user is None:
        return resp_auth_error()
    if user.is_admin() is False:
        return resp_error("没有权限", code=-98)
    d = bind_device(session, user_id, name)
    if d:
        return resp_success("已绑定")
    return resp_error("未绑定")


@router.get("/admin/unbindDevice")
def api_unbind_device(user_id: int, name: str, auth: str = Header(...)):
    user = auth_admin(session, auth)
    if user is None:
        return resp_auth_error()
    if user.is_admin() is False:
        return resp_error("没有权限", code=-98)
    d = unbind_device(session, user_id, name)
    if d:
        return resp_success("已解绑")
    return resp_error("解绑失败")


@router.get("/admin/deleteDevice")
def api_delete_device(user_id: int, name: str, auth: str = Header(...)):
    user = auth_admin(session, auth)
    if user is None:
        return resp_auth_error()
    if user.is_admin() is False:
        return resp_error("没有权限", code=-98)
    u = get_user(session, user_id)
    if u is None:
        return resp_error("未查询到用户")
    is_del = delete_device(session, user_id, name)
    if is_del:
        resp_success("已删除")
    return resp_error("未查询到设备")


@router.get("/admin/deleteUser")
def api_delete_user(user_id: int, auth: str = Header(...)):
    user = auth_admin(session, auth)
    if user is None:
        return resp_auth_error()
    if user.is_admin() is False:
        return resp_error("没有权限", code=-98)
    is_delete = delete_user(session, user_id)
    if is_delete:
        return resp_success(data="success")
    else:
        return resp_error("用户不存在")
