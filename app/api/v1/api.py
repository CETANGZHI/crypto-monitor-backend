from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, twitter, wallet, blackrock, notifications, oauth

# 创建API路由器
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(oauth.router, prefix="/oauth", tags=["OAuth认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(twitter.router, prefix="/twitter", tags=["推特监控"])
api_router.include_router(wallet.router, prefix="/wallet", tags=["钱包监控"])
api_router.include_router(blackrock.router, prefix="/blackrock", tags=["贝莱德持仓"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["通知管理"])

