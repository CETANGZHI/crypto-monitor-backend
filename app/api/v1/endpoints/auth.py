from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.crud.crud_user import user as user_crud
from app import schemas
from app.api import deps
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.core.config import settings
from app.models.user import User, UserType
from app.core.email import email_service

router = APIRouter()

@router.post("/register", response_model=schemas.TokenResponse, summary="用户注册")
async def register_user(
    user_in: schemas.UserRegister,
    db: Session = Depends(deps.get_db)
):
    # 验证邮箱验证码
    if not email_service.verify_code(user_in.email, user_in.verification_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )

    user = user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    user = user_crud.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被注册"
        )

    user = user_crud.create_user(db, obj_in=user_in)
    
    # 默认给新注册用户3天试用期
    user_crud.set_trial_period(db, user_id=user.id, days=settings.TRIAL_PERIOD_DAYS)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    return {
        "access_token": create_access_token(user.id, expires_delta=access_token_expires),
        "refresh_token": create_refresh_token(user.id, expires_delta=refresh_token_expires),
        "token_type": "bearer",
        "expires_in": access_token_expires.seconds,
        "user": user
    }

@router.post("/login", response_model=schemas.TokenResponse, summary="用户登录")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db)
):
    user = user_crud.authenticate(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    user_crud.update_last_login(db, user_id=user.id)

    return {
        "access_token": create_access_token(user.id, expires_delta=access_token_expires),
        "refresh_token": create_refresh_token(user.id, expires_delta=refresh_token_expires),
        "token_type": "bearer",
        "expires_in": access_token_expires.seconds,
        "user": user
    }

@router.post("/refresh_token", response_model=schemas.TokenResponse, summary="刷新访问令牌")
async def refresh_access_token(
    token_refresh: schemas.TokenRefresh,
    db: Session = Depends(deps.get_db)
):
    user_id = user_crud.verify_refresh_token(token_refresh.refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未找到",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(user.id, expires_delta=access_token_expires),
        "refresh_token": create_refresh_token(user.id, expires_delta=refresh_token_expires),
        "token_type": "bearer",
        "expires_in": access_token_expires.seconds,
        "user": user
    }

@router.post("/auto_register", response_model=schemas.TokenResponse, summary="自动注册")
async def auto_register_user(
    auto_register_in: schemas.AutoRegister,
    request: Request,
    db: Session = Depends(deps.get_db)
):
    if not auto_register_in.device_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="设备ID不能为空"
        )
    
    user = user_crud.get_by_device_id(db, device_id=auto_register_in.device_id)
    if user:
        # 如果设备已注册，直接返回其令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        user_crud.update_last_login(db, user_id=user.id)
        return {
            "access_token": create_access_token(user.id, expires_delta=access_token_expires),
            "refresh_token": create_refresh_token(user.id, expires_delta=refresh_token_expires),
            "token_type": "bearer",
            "expires_in": access_token_expires.seconds,
            "user": user
        }

    # 自动生成用户名和密码
    username = user_crud.generate_unique_username(db)
    password = user_crud.generate_random_password()
    email = None # 自动注册不强制邮箱

    user_create_data = {
        "username": username,
        "email": email,
        "password": password,
        "device_id": auto_register_in.device_id,
        "user_agent": auto_register_in.user_agent,
        "ip_address": request.client.host if request.client else None
    }
    user = user_crud.create_user(db, obj_in=user_create_data)
    
    # 默认给新注册用户3天试用期
    user_crud.set_trial_period(db, user_id=user.id, days=settings.TRIAL_PERIOD_DAYS)

    return {
        "access_token": create_access_token(user.id, expires_delta=access_token_expires),
        "refresh_token": create_refresh_token(user.id, expires_delta=refresh_token_expires),
        "token_type": "bearer",
        "expires_in": access_token_expires.seconds,
        "user": user
    }

@router.post("/send_verification_code", response_model=schemas.VerificationResponse, summary="发送邮箱验证码")
async def send_verification_code(
    email_in: schemas.SendVerificationCode,
    db: Session = Depends(deps.get_db)
):
    # 检查邮箱是否已注册
    user = user_crud.get_by_email(db, email=email_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    if email_service.send_verification_code(email_in.email):
        return {"success": True, "message": "验证码已发送到您的邮箱，请查收。"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="验证码发送失败，请稍后再试"
        )



