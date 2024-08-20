from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 创建数据库引擎
engine = create_engine('sqlite:///app.db', echo=False)

# 创建Session类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 创建Session实例
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
