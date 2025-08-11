from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserType, UserStatus

# 发送邮箱验证码请求模式
class SendVerificationCode(BaseModel):
    email: EmailStr = Field(..., description="邮箱地址")

# 用户注册请求模式
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    verification_code: str = Field(..., min_length=6, max_length=6, description="邮箱验证码")

# 用户登录请求模式
class UserLogin(BaseModel):
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")

# 自动注册请求模式
class AutoRegister(BaseModel):
    device_id: Optional[str] = Field(None, description="设备ID")
    user_agent: Optional[str] = Field(None, description="用户代理")

# 用户信息更新模式
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    email_notifications: Optional[bool] = Field(None, description="邮件通知")
    sms_notifications: Optional[bool] = Field(None, description="短信通知")
    push_notifications: Optional[bool] = Field(None, description="推送通知")

# 密码修改模式
class PasswordChange(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")

# 用户响应模式
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    user_type: UserType
    status: UserStatus
    max_follows: int
    current_follows: int
    email_notifications: bool
    sms_notifications: bool
    push_notifications: bool
    trial_start_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 用户简要信息模式
class UserBrief(BaseModel):
    id: int
    username: str
    user_type: UserType
    status: UserStatus
    current_follows: int
    max_follows: int
    
    class Config:
        from_attributes = True

# 令牌响应模式
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

# 令牌刷新请求模式
class TokenRefresh(BaseModel):
    refresh_token: str = Field(..., description="刷新令牌")

# 用户统计模式
class UserStats(BaseModel):
    total_users: int
    trial_users: int
    paid_users: int
    active_users: int
    new_users_today: int
    
# 试用期状态模式
class TrialStatus(BaseModel):
    is_trial: bool
    days_remaining: Optional[int] = None
    is_expired: bool
    can_upgrade: bool

# 验证码验证响应模式
class VerificationResponse(BaseModel):
    success: bool
    message: str


