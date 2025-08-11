from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    """通知类型枚举"""
    TWITTER = "twitter"
    WALLET = "wallet"
    BLACKROCK = "blackrock"
    SYSTEM = "system"

class NotificationStatus(str, Enum):
    """通知状态枚举"""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"

class NotificationPriority(str, Enum):
    """通知优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# 通知相关模式
class NotificationBase(BaseModel):
    """通知基础模式"""
    title: str = Field(..., max_length=200)
    content: str
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    related_id: Optional[str] = None
    related_data: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    """创建通知模式"""
    user_id: int

class NotificationUpdate(BaseModel):
    """更新通知模式"""
    status: Optional[NotificationStatus] = None
    read_at: Optional[datetime] = None

class NotificationResponse(NotificationBase):
    """通知响应模式"""
    id: int
    user_id: int
    status: NotificationStatus
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NotificationList(BaseModel):
    """通知列表响应模式"""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int

# 通知规则相关模式
class NotificationRuleBase(BaseModel):
    """通知规则基础模式"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    type: NotificationType
    is_active: bool = True
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    max_notifications_per_hour: int = Field(default=10, ge=1, le=100)
    max_notifications_per_day: int = Field(default=100, ge=1, le=1000)

class NotificationRuleCreate(NotificationRuleBase):
    """创建通知规则模式"""
    pass

class NotificationRuleUpdate(BaseModel):
    """更新通知规则模式"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    conditions: Optional[Dict[str, Any]] = None
    actions: Optional[Dict[str, Any]] = None
    max_notifications_per_hour: Optional[int] = Field(None, ge=1, le=100)
    max_notifications_per_day: Optional[int] = Field(None, ge=1, le=1000)

class NotificationRuleResponse(NotificationRuleBase):
    """通知规则响应模式"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_triggered_at: Optional[datetime] = None
    trigger_count: int

    class Config:
        from_attributes = True

# 通知设置相关模式
class NotificationSettingsBase(BaseModel):
    """通知设置基础模式"""
    notifications_enabled: bool = True
    twitter_notifications: bool = True
    wallet_notifications: bool = True
    blackrock_notifications: bool = True
    system_notifications: bool = True
    email_notifications: bool = True
    browser_notifications: bool = True
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = Field(default="22:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: str = Field(default="08:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    max_notifications_per_hour: int = Field(default=20, ge=1, le=100)
    max_notifications_per_day: int = Field(default=200, ge=1, le=1000)

class NotificationSettingsUpdate(NotificationSettingsBase):
    """更新通知设置模式"""
    pass

class NotificationSettingsResponse(NotificationSettingsBase):
    """通知设置响应模式"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 通知模板相关模式
class NotificationTemplateBase(BaseModel):
    """通知模板基础模式"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    type: NotificationType
    title_template: str = Field(..., max_length=200)
    content_template: str
    variables: Optional[Dict[str, str]] = None
    is_active: bool = True

class NotificationTemplateCreate(NotificationTemplateBase):
    """创建通知模板模式"""
    pass

class NotificationTemplateUpdate(BaseModel):
    """更新通知模板模式"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    title_template: Optional[str] = Field(None, max_length=200)
    content_template: Optional[str] = None
    variables: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None

class NotificationTemplateResponse(NotificationTemplateBase):
    """通知模板响应模式"""
    id: int
    is_system: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 批量操作模式
class NotificationBatchUpdate(BaseModel):
    """批量更新通知模式"""
    notification_ids: List[int]
    status: NotificationStatus

class NotificationBatchDelete(BaseModel):
    """批量删除通知模式"""
    notification_ids: List[int]

# 统计模式
class NotificationStats(BaseModel):
    """通知统计模式"""
    total_notifications: int
    unread_count: int
    read_count: int
    archived_count: int
    notifications_by_type: Dict[str, int]
    notifications_by_priority: Dict[str, int]
    recent_notifications: List[NotificationResponse]

