from sqlalchemy.orm import Session
from app.db.base import engine, Base
from app.models.user import User, UserType, UserStatus
from app.core.security import get_password_hash
from datetime import datetime, timedelta
from app.core.config import settings

def init_db() -> None:
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")

def create_sample_data() -> None:
    """创建示例数据"""
    from app.db.base import SessionLocal
    
    db = SessionLocal()
    
    try:
        # 检查是否已有用户数据
        existing_user = db.query(User).first()
        if existing_user:
            print("📊 数据库中已存在用户数据，跳过示例数据创建")
            return
        
        # 创建管理员用户
        admin_user = User(
            username="admin",
            email="admin@crypto-monitor.com",
            hashed_password=get_password_hash("admin123"),
            user_type=UserType.LIFETIME,
            status=UserStatus.ACTIVE,
            max_follows=999,
            current_follows=0,
            email_notifications=True,
            sms_notifications=False,
            push_notifications=True,
            created_at=datetime.utcnow(),
            last_login_at=datetime.utcnow()
        )
        
        # 创建试用用户
        trial_end_date = datetime.utcnow() + timedelta(days=settings.TRIAL_PERIOD_DAYS)
        trial_user = User(
            username="试用用户001",
            email="trial@example.com",
            hashed_password=get_password_hash("trial123"),
            user_type=UserType.TRIAL,
            status=UserStatus.ACTIVE,
            trial_end_date=trial_end_date,
            max_follows=settings.TRIAL_MAX_FOLLOWS,
            current_follows=2,
            email_notifications=True,
            sms_notifications=False,
            push_notifications=True,
            created_at=datetime.utcnow(),
            last_login_at=datetime.utcnow()
        )
        
        # 创建付费用户
        subscription_end_date = datetime.utcnow() + timedelta(days=30)
        paid_user = User(
            username="付费用户001",
            email="paid@example.com",
            phone="13800138000",
            hashed_password=get_password_hash("paid123"),
            user_type=UserType.MONTHLY,
            status=UserStatus.ACTIVE,
            subscription_start_date=datetime.utcnow(),
            subscription_end_date=subscription_end_date,
            max_follows=999,
            current_follows=15,
            email_notifications=True,
            sms_notifications=True,
            push_notifications=True,
            created_at=datetime.utcnow(),
            last_login_at=datetime.utcnow()
        )
        
        # 创建自动注册用户
        auto_user = User(
            username="用户123456",
            device_id="device_12345678",
            user_type=UserType.TRIAL,
            status=UserStatus.ACTIVE,
            trial_end_date=trial_end_date,
            max_follows=settings.TRIAL_MAX_FOLLOWS,
            current_follows=1,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            created_at=datetime.utcnow(),
            last_login_at=datetime.utcnow()
        )
        
        # 添加到数据库
        db.add_all([admin_user, trial_user, paid_user, auto_user])
        db.commit()
        
        print("✅ 示例用户数据创建完成:")
        print(f"   - 管理员: admin / admin123")
        print(f"   - 试用用户: 试用用户001 / trial123")
        print(f"   - 付费用户: 付费用户001 / paid123")
        print(f"   - 自动注册用户: 用户123456 (无密码)")
        
    except Exception as e:
        print(f"❌ 创建示例数据失败: {e}")
        db.rollback()
    finally:
        db.close()

def reset_db() -> None:
    """重置数据库（删除所有表并重新创建）"""
    Base.metadata.drop_all(bind=engine)
    print("🗑️  数据库表已删除")
    init_db()

if __name__ == "__main__":
    print("🚀 开始初始化数据库...")
    init_db()
    create_sample_data()
    print("🎉 数据库初始化完成！")

