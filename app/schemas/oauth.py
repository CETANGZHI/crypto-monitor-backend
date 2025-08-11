from pydantic import BaseModel, EmailStr
from typing import Optional

class OAuthUserInfo(BaseModel):
    """OAuth用户信息模式"""
    provider: str  # google, apple
    provider_id: str
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None
    email_verified: bool = False

class GoogleOAuthRequest(BaseModel):
    """Google OAuth请求模式"""
    id_token: str
    access_token: Optional[str] = None

class AppleOAuthRequest(BaseModel):
    """Apple OAuth请求模式"""
    id_token: str
    authorization_code: str
    user: Optional[dict] = None

class OAuthLoginResponse(BaseModel):
    """OAuth登录响应模式"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict
    is_new_user: bool = False  # 是否为新用户

class OAuthCallbackRequest(BaseModel):
    """OAuth回调请求模式"""
    code: str
    state: Optional[str] = None
    error: Optional[str] = None
    error_description: Optional[str] = None

