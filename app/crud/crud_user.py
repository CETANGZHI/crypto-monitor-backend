from typing import Any, Dict, Optional, Union, List
from datetime import datetime, timedelta
import random
import string

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserType, UserStatus
from app.schemas.user import UserRegister, UserUpdate, AutoRegister
from app.core.config import settings

class CRUDUser:
    def get(self, db: Session, id: int) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_by_device_id(self, db: Session, device_id: str) -> Optional[User]:
        return db.query(User).filter(User.device_id == device_id).first()

    def create_user(self, db: Session, obj_in: UserRegister) -> User:
        hashed_password = get_password_hash(obj_in.password)
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            hashed_password=hashed_password,
            user_type=UserType.TRIAL, # 默认试用用户
            status=UserStatus.ACTIVE,
            max_follows=settings.TRIAL_MAX_FOLLOWS, # 试用用户关注上限
            trial_start_date=datetime.utcnow(),
            trial_end_date=datetime.utcnow() + timedelta(days=settings.TRIAL_PERIOD_DAYS),
            created_at=datetime.utcnow(),
            last_login_at=datetime.utcnow()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_auto_user(self, db: Session, obj_in: AutoRegister, ip_address: Optional[str] = None) -> User:
        username = self.generate_unique_username(db)
        password = self.generate_random_password() # 自动注册用户生成随机密码
        hashed_password = get_password_hash(password)

        db_obj = User(
            username=username,
            email=None, # 自动注册用户没有邮箱
            hashed_password=hashed_password,
            user_type=UserType.TRIAL,
            status=UserStatus.ACTIVE,
            device_id=obj_in.device_id,
            user_agent=obj_in.user_agent,
            ip_address=ip_address,
            max_follows=settings.TRIAL_MAX_FOLLOWS,
            trial_start_date=datetime.utcnow(),
            trial_end_date=datetime.utcnow() + timedelta(days=settings.TRIAL_PERIOD_DAYS),
            created_at=datetime.utcnow(),
            last_login_at=datetime.utcnow()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def update_user(self, db: Session, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            del update_data["password"]

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_last_login(self, db: Session, user_id: int) -> Optional[User]:
        user = self.get(db, user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def set_trial_period(self, db: Session, user_id: int, days: int) -> Optional[User]:
        user = self.get(db, user_id)
        if user:
            user.trial_start_date = datetime.utcnow()
            user.trial_end_date = datetime.utcnow() + timedelta(days=days)
            user.user_type = UserType.TRIAL
            user.max_follows = settings.TRIAL_MAX_FOLLOWS
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def generate_unique_username(self, db: Session) -> str:
        while True:
            username = "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
            if not self.get_by_username(db, username):
                return username

    def generate_random_password(self) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=12))

    def get_by_oauth_provider(self, db: Session, provider: str, provider_id: str) -> Optional[User]:
        """通过OAuth提供商和ID查找用户"""
        return db.query(User).filter(
            User.oauth_provider == provider,
            User.oauth_provider_id == provider_id
        ).first()

    def create_oauth_user(self, db: Session, oauth_info: dict) -> User:
        """创建OAuth用户"""
        # 生成唯一用户名
        username = self.generate_unique_username(db)
        
        db_obj = User(
            username=username,
            email=oauth_info.get('email'),
            hashed_password=None,  # OAuth用户没有密码
            user_type=UserType.TRIAL,
            status=UserStatus.ACTIVE,
            oauth_provider=oauth_info.get('provider'),
            oauth_provider_id=oauth_info.get('provider_id'),
            oauth_email_verified=oauth_info.get('email_verified', False),
            max_follows=settings.TRIAL_MAX_FOLLOWS,
            trial_start_date=datetime.utcnow(),
            trial_end_date=datetime.utcnow() + timedelta(days=settings.TRIAL_PERIOD_DAYS),
            created_at=datetime.utcnow(),
            last_login_at=datetime.utcnow()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def link_oauth_account(self, db: Session, user: User, oauth_info: dict) -> User:
        """将OAuth账号链接到现有用户"""
        user.oauth_provider = oauth_info.get('provider')
        user.oauth_provider_id = oauth_info.get('provider_id')
        user.oauth_email_verified = oauth_info.get('email_verified', False)
        user.updated_at = datetime.utcnow()
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def verify_refresh_token(self, refresh_token: str) -> Optional[int]:
        # 这是一个简化的验证，实际生产环境需要更复杂的刷新令牌管理
        # 例如，将刷新令牌存储在数据库中，并与用户关联，支持撤销等
        try:
            payload = verify_password(refresh_token, settings.SECRET_KEY) # 这里应该用单独的refresh token secret
            user_id = payload.get("sub")
            if user_id:
                return int(user_id)
        except Exception:
            return None
        return None

user = CRUDUser()


