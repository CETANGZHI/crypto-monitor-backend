from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 创建数据库引擎
# 开发阶段使用SQLite，生产环境可切换到PostgreSQL
SQLALCHEMY_DATABASE_URL = "sqlite:///./crypto_monitor.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite特定配置
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# 注意：不要在这里导入模型，避免循环导入
# 模型导入应该在需要时进行

