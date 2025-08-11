from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from datetime import datetime, timedelta

from app.db.base import Base

# 使用统一的Base
try:
    from app.db.base import Base
except ImportError:
    Base = declarative_base()

class UserType(str, PyEnum):
    """用户类型枚举"""
    TRIAL = "trial"      # 试用用户
    MONTHLY = "monthly"  # 月付用户
    YEARLY = "yearly"    # 年付用户
    LIFETIME = "lifetime" # 终身用户

class UserStatus(str, PyEnum):
    """用户状态枚举"""
    ACTIVE = "active"       # 活跃
    INACTIVE = "inactive"   # 非活跃
    SUSPENDED = "suspended" # 暂停
    EXPIRED = "expired"     # 过期

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    
    # 用户类型和状态
    user_type = Column(Enum(UserType), default=UserType.TRIAL, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    
    # 设备信息（用于自动注册）
    device_id = Column(String(100), unique=True, index=True, nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # OAuth信息
    oauth_provider = Column(String(20), nullable=True)  # google, apple
    oauth_provider_id = Column(String(100), nullable=True)
    oauth_email_verified = Column(Boolean, default=False)
    
    # 试用期信息
    trial_start_date = Column(DateTime(timezone=True), server_default=func.now())
    trial_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # 订阅信息
    subscription_start_date = Column(DateTime(timezone=True), nullable=True)
    subscription_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # 使用统计
    max_follows = Column(Integer, default=5)  # 最大关注数量
    current_follows = Column(Integer, default=0)  # 当前关注数量
    
    # 通知设置
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username=\\'{self.username}\\, type=\\'{self.user_type}\\,)>"
    
    @property
    def is_trial_expired(self) -> bool:
        """检查试用期是否过期"""
        if self.user_type != UserType.TRIAL:
            return False
        if not self.trial_end_date:
            return False
        from datetime import datetime
        return datetime.utcnow() > self.trial_end_date
    
    @property
    def is_subscription_active(self) -> bool:
        """检查订阅是否有效"""
        if self.user_type == UserType.TRIAL:
            return not self.is_trial_expired
        if self.user_type == UserType.LIFETIME:
            return True
        if not self.subscription_end_date:
            return False
        from datetime import datetime
        return datetime.utcnow() <= self.subscription_end_date
    
    @property
    def can_add_follows(self) -> bool:
        """检查是否可以添加更多关注"""
        return self.current_follows < self.max_follows

    # 关联关系
    notifications = relationship("Notification", back_populates="user")
    notification_rules = relationship("NotificationRule", back_populates="user")
    notification_settings = relationship("NotificationSettings", back_populates="user", uselist=False)



