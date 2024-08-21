import logging
import uuid
from typing import Type, Optional

from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship

from server.util.md5 import md5

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
engine = create_engine('sqlite:///app.db', echo=True)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, unique=True)
    password = Column(String)
    auth_token = Column(String)

    devices = relationship("Device", back_populates="user")

    def is_admin(self) -> bool:
        return self.username == 'admin'

    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "authToken": self.auth_token
        }

    def simple_user(self):
        return {
            "id": self.id,
            "username": self.username
        }


class Device(Base):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True)
    device_name = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    # Relationship
    user = relationship("User", back_populates="devices")


Base.metadata.create_all(engine)


# 添加用户
def add_user(db: Session, username: str, password: str) -> tuple[Optional[str], Optional[User]]:
    try:
        user = User(username=username, password=md5(password))
        user.devices = []
        db.add(user)
        db.commit()
        db.refresh(user)
        return None, user
    except Exception:
        db.rollback()
    return "用户已存在", None


def login_user(db: Session, username: str, password: str) -> Optional[User]:
    pwd = md5(password)
    user = db.query(User).filter_by(username=username, password=pwd).first()
    if user:
        if user.password is None or user.auth_token is None:
            user.auth_token = str(uuid.uuid4())
            user.password = pwd
            db.commit()
            db.refresh(user)
    return user


# 查询用户
def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


def auth_user(db: Session, auth_token: str) -> Optional[User]:
    user = db.query(User).filter_by(auth_token=auth_token).first()
    return user


def auth_admin(db: Session, auth_token: str) -> Optional[User]:
    user = db.query(User).filter_by(auth_token=auth_token).first()
    if user and user.is_admin() is True:
        return user
    return None


def delete_user(db: Session, user_id: int):
    user = db.query(User).filter_by(id=user_id).first()
    if user:
        db.delete(user)  # 删除记录
        db.commit()
        return True
    else:
        return False


def delete_device(db: Session, user_id: int, name: str) -> bool:
    user = db.query(User).filter_by(id=user_id).first()
    device_to_delete = db.query(Device).filter_by(device_name=name, user_id=user_id).first()
    # 从用户的 devices 集合中删除设备
    if user and device_to_delete:
        user.devices.remove(device_to_delete)
        db.delete(device_to_delete)
        db.commit()
        return True
    return False


def bind_device(db: Session, user_id: int, name: str) -> bool:
    user = db.query(User).filter_by(id=user_id).first()
    device_to_bind = db.query(Device).filter_by(device_name=name, user_id=user_id).first()
    if not User:
        return False
    if not device_to_bind:
        user.devices.append(Device(device_name=name))
        db.commit()
        return True
    return False


def unbind_device(db: Session, user_id: int, name: str) -> bool:
    user = db.query(User).filter_by(id=user_id).first()
    device_to_unbind = db.query(Device).filter_by(device_name=name, user_id=user_id).first()
    # 从用户的 devices 集合中删除设备
    if not User:
        return False
    if device_to_unbind:
        user.devices.remove(device_to_unbind)
        db.delete(device_to_unbind)
        db.commit()
        return True
    return False


# 查询用户
def get_users(db: Session):
    users = db.query(User).all()
    user_list = []
    for user in users:
        user_list.append(user.simple_user())
    return user_list


def update_user(db: Session, auth_token: str, password: str) -> tuple[Optional[str], Optional[Type[User]]]:
    if auth_token is None or password is None:
        return "密码不能为空", None
    if len(password) < 6:
        return "密码不能小于6位", None

    try:
        user = db.query(User).filter_by(auth_token=auth_token).first()
        if user is None or user.id is None:
            return "未查询到用户", None
        user.password = md5(password)
        user.auth_token = str(uuid.uuid4())
        db.commit()
        db.refresh(user)
        return None, user
    except Exception:
        db.rollback()
    return "更新异常,请稍后再试", None
