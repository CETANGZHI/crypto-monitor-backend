from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from app.db.base import Base

class NotificationType(PyEnum):
    """通知类型枚举"""
    TWITTER = "twitter"  # 推特通知
    WALLET = "wallet"    # 钱包通知
    BLACKROCK = "blackrock"  # 贝莱德持仓通知
    SYSTEM = "system"    # 系统通知

class NotificationStatus(PyEnum):
    """通知状态枚举"""
    UNREAD = "unread"    # 未读
    READ = "read"        # 已读
    ARCHIVED = "archived"  # 已归档

class NotificationPriority(PyEnum):
    """通知优先级枚举"""
    LOW = "low"          # 低优先级
    MEDIUM = "medium"    # 中优先级
    HIGH = "high"        # 高优先级
    URGENT = "urgent"    # 紧急

class Notification(Base):
    """通知表"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 通知基本信息
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(Enum(NotificationType), nullable=False, index=True)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.UNREAD, index=True)
    
    # 相关数据
    related_id = Column(String(100), nullable=True)  # 相关对象ID（如推特ID、钱包地址等）
    related_data = Column(Text, nullable=True)  # 相关数据的JSON字符串
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关联关系
    user = relationship("User", back_populates="notifications")

class NotificationRule(Base):
    """通知规则表"""
    __tablename__ = "notification_rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 规则基本信息
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(NotificationType), nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # 规则配置
    conditions = Column(Text, nullable=False)  # 触发条件的JSON字符串
    actions = Column(Text, nullable=False)     # 执行动作的JSON字符串
    
    # 频率控制
    max_notifications_per_hour = Column(Integer, default=10)
    max_notifications_per_day = Column(Integer, default=100)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    
    # 统计信息
    trigger_count = Column(Integer, default=0)
    
    # 关联关系
    user = relationship("User", back_populates="notification_rules")

class NotificationSettings(Base):
    """通知设置表"""
    __tablename__ = "notification_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # 全局通知开关
    notifications_enabled = Column(Boolean, default=True)
    
    # 各类型通知开关
    twitter_notifications = Column(Boolean, default=True)
    wallet_notifications = Column(Boolean, default=True)
    blackrock_notifications = Column(Boolean, default=True)
    system_notifications = Column(Boolean, default=True)
    
    # 通知方式设置
    email_notifications = Column(Boolean, default=True)
    browser_notifications = Column(Boolean, default=True)
    
    # 免打扰时间设置
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5), default="22:00")  # HH:MM格式
    quiet_hours_end = Column(String(5), default="08:00")    # HH:MM格式
    
    # 频率限制
    max_notifications_per_hour = Column(Integer, default=20)
    max_notifications_per_day = Column(Integer, default=200)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="notification_settings")

class NotificationTemplate(Base):
    """通知模板表"""
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    
    # 模板基本信息
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    type = Column(Enum(NotificationType), nullable=False, index=True)
    
    # 模板内容
    title_template = Column(String(200), nullable=False)
    content_template = Column(Text, nullable=False)
    
    # 模板变量说明
    variables = Column(Text, nullable=True)  # 可用变量的JSON字符串
    
    # 状态
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # 是否为系统模板
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

