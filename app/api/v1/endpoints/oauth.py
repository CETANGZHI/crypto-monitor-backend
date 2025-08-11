from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta

from app.crud.crud_user import user as user_crud
from app import schemas
from app.api import deps
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings
from app.core.oauth import oauth_service
from app.models.user import User

router = APIRouter()

@router.post("/google/login", response_model=schemas.OAuthLoginResponse, summary="Google OAuth登录")
async def google_oauth_login(
    oauth_request: schemas.GoogleOAuthRequest,
    db: Session = Depends(deps.get_db)
):
    """
    Google OAuth登录
    
    - **id_token**: Google ID Token
    - **access_token**: Google Access Token (可选)
    """
    try:
        # 验证Google ID Token并获取用户信息
        user_info = await oauth_service.get_google_user_info(oauth_request.id_token)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的Google令牌"
            )
        
        # 检查是否已存在OAuth用户
        existing_user = user_crud.get_by_oauth_provider(
            db, 
            provider=user_info['provider'], 
            provider_id=user_info['provider_id']
        )
        
        is_new_user = False
        
        if existing_user:
            # 用户已存在，直接登录
            user = existing_user
            user_crud.update_last_login(db, user_id=user.id)
        else:
            # 检查是否有相同邮箱的用户
            email_user = user_crud.get_by_email(db, email=user_info['email'])
            
            if email_user:
                # 邮箱已存在，链接OAuth账号
                user = user_crud.link_oauth_account(db, email_user, user_info)
            else:
                # 创建新用户
                user = user_crud.create_oauth_user(db, user_info)
                is_new_user = True
        
        # 生成令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        
        return schemas.OAuthLoginResponse(
            access_token=create_access_token(user.id, expires_delta=access_token_expires),
            refresh_token=create_refresh_token(user.id, expires_delta=refresh_token_expires),
            expires_in=access_token_expires.seconds,
            user=schemas.UserResponse.from_orm(user),
            is_new_user=is_new_user
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google登录失败: {str(e)}"
        )

@router.post("/apple/login", response_model=schemas.OAuthLoginResponse, summary="Apple OAuth登录")
async def apple_oauth_login(
    oauth_request: schemas.AppleOAuthRequest,
    db: Session = Depends(deps.get_db)
):
    """
    Apple OAuth登录
    
    - **id_token**: Apple ID Token
    - **authorization_code**: Apple Authorization Code
    - **user**: Apple用户信息 (可选)
    """
    try:
        # 验证Apple ID Token并获取用户信息
        user_info = await oauth_service.get_apple_user_info(oauth_request.id_token)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的Apple令牌"
            )
        
        # 如果Apple提供了额外的用户信息，使用它
        if oauth_request.user:
            apple_user_data = oauth_request.user
            if 'name' in apple_user_data:
                name_data = apple_user_data['name']
                full_name = f"{name_data.get('firstName', '')} {name_data.get('lastName', '')}".strip()
                if full_name:
                    user_info['name'] = full_name
        
        # 检查是否已存在OAuth用户
        existing_user = user_crud.get_by_oauth_provider(
            db, 
            provider=user_info['provider'], 
            provider_id=user_info['provider_id']
        )
        
        is_new_user = False
        
        if existing_user:
            # 用户已存在，直接登录
            user = existing_user
            user_crud.update_last_login(db, user_id=user.id)
        else:
            # 检查是否有相同邮箱的用户
            email_user = user_crud.get_by_email(db, email=user_info['email'])
            
            if email_user:
                # 邮箱已存在，链接OAuth账号
                user = user_crud.link_oauth_account(db, email_user, user_info)
            else:
                # 创建新用户
                user = user_crud.create_oauth_user(db, user_info)
                is_new_user = True
        
        # 生成令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        
        return schemas.OAuthLoginResponse(
            access_token=create_access_token(user.id, expires_delta=access_token_expires),
            refresh_token=create_refresh_token(user.id, expires_delta=refresh_token_expires),
            expires_in=access_token_expires.seconds,
            user=schemas.UserResponse.from_orm(user),
            is_new_user=is_new_user
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Apple登录失败: {str(e)}"
        )

@router.get("/google/authorize", summary="Google OAuth授权URL")
async def google_authorize_url(request: Request):
    """
    获取Google OAuth授权URL
    """
    try:
        google = oauth_service.get_google_client()
        redirect_uri = f"{settings.FRONTEND_URL}/auth/google/callback"
        
        authorization_url = await google.create_authorization_url(
            redirect_uri,
            scope='openid email profile'
        )
        
        return {
            "authorization_url": authorization_url['url'],
            "state": authorization_url.get('state')
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成Google授权URL失败: {str(e)}"
        )

@router.get("/apple/authorize", summary="Apple OAuth授权URL")
async def apple_authorize_url(request: Request):
    """
    获取Apple OAuth授权URL
    """
    try:
        apple = oauth_service.get_apple_client()
        redirect_uri = f"{settings.FRONTEND_URL}/auth/apple/callback"
        
        authorization_url = await apple.create_authorization_url(
            redirect_uri,
            scope='name email',
            response_mode='form_post'
        )
        
        return {
            "authorization_url": authorization_url['url'],
            "state": authorization_url.get('state')
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成Apple授权URL失败: {str(e)}"
        )

@router.post("/google/callback", response_model=schemas.OAuthLoginResponse, summary="Google OAuth回调")
async def google_oauth_callback(
    callback_request: schemas.OAuthCallbackRequest,
    db: Session = Depends(deps.get_db)
):
    """
    Google OAuth回调处理
    
    - **code**: 授权码
    - **state**: 状态参数
    """
    if callback_request.error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth授权失败: {callback_request.error_description or callback_request.error}"
        )
    
    try:
        google = oauth_service.get_google_client()
        redirect_uri = f"{settings.FRONTEND_URL}/auth/google/callback"
        
        # 交换授权码获取令牌
        token = await google.authorize_access_token(
            code=callback_request.code,
            redirect_uri=redirect_uri
        )
        
        # 获取用户信息
        user_info = await oauth_service.get_google_user_info(token['id_token'])
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法获取Google用户信息"
            )
        
        # 处理用户登录/注册逻辑（与直接登录相同）
        existing_user = user_crud.get_by_oauth_provider(
            db, 
            provider=user_info['provider'], 
            provider_id=user_info['provider_id']
        )
        
        is_new_user = False
        
        if existing_user:
            user = existing_user
            user_crud.update_last_login(db, user_id=user.id)
        else:
            email_user = user_crud.get_by_email(db, email=user_info['email'])
            
            if email_user:
                user = user_crud.link_oauth_account(db, email_user, user_info)
            else:
                user = user_crud.create_oauth_user(db, user_info)
                is_new_user = True
        
        # 生成令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        
        return schemas.OAuthLoginResponse(
            access_token=create_access_token(user.id, expires_delta=access_token_expires),
            refresh_token=create_refresh_token(user.id, expires_delta=refresh_token_expires),
            expires_in=access_token_expires.seconds,
            user=schemas.UserResponse.from_orm(user),
            is_new_user=is_new_user
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google回调处理失败: {str(e)}"
        )

