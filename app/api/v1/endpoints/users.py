from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.user import (
    UserResponse, 
    UserUpdate, 
    PasswordChange,
    UserBrief
)
from app.models.user import User
from app.api.deps import get_db, get_current_user
from app.core.security import verify_password, get_password_hash

router = APIRouter()

@router.get("/profile", response_model=UserResponse, summary="获取用户资料")
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的详细资料"""
    return UserResponse.from_orm(current_user)

@router.put("/profile", response_model=UserResponse, summary="更新用户资料")
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户资料
    - 可更新用户名、邮箱、手机号
    - 可更新通知设置
    """
    # 检查用户名是否已被其他用户使用
    if user_update.username and user_update.username != current_user.username:
        existing_user = db.query(User).filter(
            User.username == user_update.username,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被使用"
            )
        current_user.username = user_update.username
    
    # 检查邮箱是否已被其他用户使用
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
        current_user.email = user_update.email
    
    # 检查手机号是否已被其他用户使用
    if user_update.phone and user_update.phone != current_user.phone:
        existing_user = db.query(User).filter(
            User.phone == user_update.phone,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被使用"
            )
        current_user.phone = user_update.phone
    
    # 更新通知设置
    if user_update.email_notifications is not None:
        current_user.email_notifications = user_update.email_notifications
    
    if user_update.sms_notifications is not None:
        current_user.sms_notifications = user_update.sms_notifications
    
    if user_update.push_notifications is not None:
        current_user.push_notifications = user_update.push_notifications
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)

@router.post("/change-password", summary="修改密码")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改用户密码
    - 验证旧密码
    - 设置新密码
    """
    # 检查是否有设置密码（自动注册用户可能没有密码）
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户未设置密码，请先设置密码"
        )
    
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 设置新密码
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "密码修改成功"}

@router.post("/set-password", summary="设置密码")
async def set_password(
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    为自动注册用户设置密码
    - 仅限未设置密码的用户
    """
    if current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已设置密码，请使用修改密码功能"
        )
    
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度至少6位"
        )
    
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "密码设置成功"}

@router.get("/subscription-status", summary="获取订阅状态")
async def get_subscription_status(
    current_user: User = Depends(get_current_user)
):
    """获取用户的订阅状态信息"""
    return {
        "user_type": current_user.user_type,
        "status": current_user.status,
        "is_trial": current_user.user_type.value == "trial",
        "is_trial_expired": current_user.is_trial_expired,
        "is_subscription_active": current_user.is_subscription_active,
        "trial_end_date": current_user.trial_end_date,
        "subscription_end_date": current_user.subscription_end_date,
        "max_follows": current_user.max_follows,
        "current_follows": current_user.current_follows,
        "can_add_follows": current_user.can_add_follows
    }

@router.delete("/account", summary="删除账户")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除用户账户
    - 软删除，将状态设为非活跃
    - 保留数据用于审计
    """
    from app.models.user import UserStatus
    
    current_user.status = UserStatus.INACTIVE
    current_user.email = None  # 清除敏感信息
    current_user.phone = None
    db.commit()
    
    return {"message": "账户已删除"}

@router.get("/usage-stats", summary="获取使用统计")
async def get_usage_stats(
    current_user: User = Depends(get_current_user)
):
    """获取用户的使用统计信息"""
    # TODO: 实现详细的使用统计
    return {
        "follows_count": current_user.current_follows,
        "max_follows": current_user.max_follows,
        "notifications_today": 0,  # 待实现
        "last_login": current_user.last_login_at,
        "account_age_days": (current_user.created_at - current_user.created_at).days if current_user.created_at else 0
    }

