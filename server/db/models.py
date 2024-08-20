import uuid

from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship

from server.util.md5 import md5

engine = create_engine('sqlite:///app.db', echo=True)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, unique=True)
    password = Column(String)
    auth_token = Column(String)

    devices = relationship("Device", back_populates="user")

    def is_admin(self):
        return self.username == 'admin'

    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "authToken": self.auth_token
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
def add_user(db: Session, username: str, password: str):
    try:
        user = User(username=username, password=md5(password))
        user.devices = [Device(device_name="9157"),
                        Device(device_name='9156'),
                        Device(device_name='9158')
                        ]
        db.add(user)
        db.commit()
        db.refresh(user)
        return None, user
    except Exception:
        db.rollback()
        print(username, "用户已存在")
    return "用户已存在", None


def login_user(db: Session, username: str, password: str):
    pwd = md5(password)
    user = db.query(User).filter(User.username == username, User.password == pwd).first()
    if user is not None:
        print("login_user", user.password, user.auth_token)
        if user.password is None or user.auth_token is None:
            user.auth_token = str(uuid.uuid4())
            user.password = pwd
            db.commit()
            db.refresh(user)
    return user


# 查询用户
def get_user(db: Session, user_id: int):
    return db.get(User, user_id)


def auth_user(db: Session, auth_token: str):
    user = db.query(User).filter(User.auth_token == auth_token).first()
    if user is None:
        return False, user
    return True, user


def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id)
    print("delete_user", user)
    user.delete()
    # 提交事务
    db.commit()


# 查询用户
def get_users(db: Session):
    users = db.query(User).all()
    for user in users:
        print("get_users", user.id, user.username, user.password, user.auth_token)
        for device in user.devices:
            print(f"Device: {device.device_name}")
    return users


def update_user(db: Session, auth_token: str, password: str):
    if auth_token is None or password is None:
        return "密码不能为空", None
    if len(password) < 6:
        return "密码不能小于6位", None

    try:
        user = db.query(User).filter(User.auth_token == auth_token).first()
        if user is None or user.id is None:
            print("update_user", "NONE")
            return "未查询到用户", None
        print("update_user", user.id, user.username)
        user.password = password
        user.auth_token = str(uuid.uuid4())
        db.commit()
        db.refresh(user)
        return None, user
    except Exception:
        db.rollback()
    return "更新异常,请稍后再试", None
