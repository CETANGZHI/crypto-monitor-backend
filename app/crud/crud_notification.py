from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.notification import (
    Notification, 
    NotificationRule, 
    NotificationSettings, 
    NotificationTemplate,
    NotificationType,
    NotificationStatus,
    NotificationPriority
)
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationRuleCreate,
    NotificationRuleUpdate,
    NotificationSettingsUpdate,
    NotificationTemplateCreate,
    NotificationTemplateUpdate
)

class CRUDNotification:
    """通知CRUD操作类"""
    
    def create(self, db: Session, obj_in: NotificationCreate) -> Notification:
        """创建通知"""
        db_obj = Notification(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Notification]:
        """根据ID获取通知"""
        return db.query(Notification).filter(Notification.id == id).first()
    
    def get_by_user(
        self, 
        db: Session, 
        user_id: int, 
        status: Optional[NotificationStatus] = None,
        type: Optional[NotificationType] = None,
        skip: int = 0, 
        limit: int = 20
    ) -> List[Notification]:
        """获取用户的通知列表"""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if status:
            query = query.filter(Notification.status == status)
        if type:
            query = query.filter(Notification.type == type)
            
        return query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()
    
    def get_unread_count(self, db: Session, user_id: int) -> int:
        """获取用户未读通知数量"""
        return db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.status == NotificationStatus.UNREAD
            )
        ).count()
    
    def update(self, db: Session, db_obj: Notification, obj_in: NotificationUpdate) -> Notification:
        """更新通知"""
        update_data = obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def mark_as_read(self, db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
        """标记通知为已读"""
        notification = db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()
        
        if notification:
            notification.status = NotificationStatus.READ
            notification.read_at = datetime.utcnow()
            db.add(notification)
            db.commit()
            db.refresh(notification)
        
        return notification
    
    def mark_all_as_read(self, db: Session, user_id: int) -> int:
        """标记用户所有通知为已读"""
        count = db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.status == NotificationStatus.UNREAD
            )
        ).update({
            "status": NotificationStatus.READ,
            "read_at": datetime.utcnow()
        })
        db.commit()
        return count
    
    def delete(self, db: Session, id: int, user_id: int) -> bool:
        """删除通知"""
        notification = db.query(Notification).filter(
            and_(
                Notification.id == id,
                Notification.user_id == user_id
            )
        ).first()
        
        if notification:
            db.delete(notification)
            db.commit()
            return True
        return False
    
    def batch_update_status(
        self, 
        db: Session, 
        notification_ids: List[int], 
        user_id: int, 
        status: NotificationStatus
    ) -> int:
        """批量更新通知状态"""
        count = db.query(Notification).filter(
            and_(
                Notification.id.in_(notification_ids),
                Notification.user_id == user_id
            )
        ).update({"status": status})
        db.commit()
        return count
    
    def get_stats(self, db: Session, user_id: int) -> Dict[str, Any]:
        """获取通知统计信息"""
        total = db.query(Notification).filter(Notification.user_id == user_id).count()
        unread = db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.status == NotificationStatus.UNREAD
            )
        ).count()
        read = db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.status == NotificationStatus.READ
            )
        ).count()
        archived = db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.status == NotificationStatus.ARCHIVED
            )
        ).count()
        
        # 按类型统计
        type_stats = db.query(
            Notification.type,
            func.count(Notification.id)
        ).filter(Notification.user_id == user_id).group_by(Notification.type).all()
        
        # 按优先级统计
        priority_stats = db.query(
            Notification.priority,
            func.count(Notification.id)
        ).filter(Notification.user_id == user_id).group_by(Notification.priority).all()
        
        return {
            "total_notifications": total,
            "unread_count": unread,
            "read_count": read,
            "archived_count": archived,
            "notifications_by_type": {str(t): c for t, c in type_stats},
            "notifications_by_priority": {str(p): c for p, c in priority_stats}
        }

class CRUDNotificationRule:
    """通知规则CRUD操作类"""
    
    def create(self, db: Session, obj_in: NotificationRuleCreate, user_id: int) -> NotificationRule:
        """创建通知规则"""
        obj_data = obj_in.dict()
        obj_data["user_id"] = user_id
        db_obj = NotificationRule(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int, user_id: int) -> Optional[NotificationRule]:
        """获取通知规则"""
        return db.query(NotificationRule).filter(
            and_(
                NotificationRule.id == id,
                NotificationRule.user_id == user_id
            )
        ).first()
    
    def get_by_user(self, db: Session, user_id: int, is_active: Optional[bool] = None) -> List[NotificationRule]:
        """获取用户的通知规则列表"""
        query = db.query(NotificationRule).filter(NotificationRule.user_id == user_id)
        
        if is_active is not None:
            query = query.filter(NotificationRule.is_active == is_active)
            
        return query.order_by(desc(NotificationRule.created_at)).all()
    
    def update(self, db: Session, db_obj: NotificationRule, obj_in: NotificationRuleUpdate) -> NotificationRule:
        """更新通知规则"""
        update_data = obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int, user_id: int) -> bool:
        """删除通知规则"""
        rule = db.query(NotificationRule).filter(
            and_(
                NotificationRule.id == id,
                NotificationRule.user_id == user_id
            )
        ).first()
        
        if rule:
            db.delete(rule)
            db.commit()
            return True
        return False

class CRUDNotificationSettings:
    """通知设置CRUD操作类"""
    
    def get_or_create(self, db: Session, user_id: int) -> NotificationSettings:
        """获取或创建用户通知设置"""
        settings = db.query(NotificationSettings).filter(
            NotificationSettings.user_id == user_id
        ).first()
        
        if not settings:
            settings = NotificationSettings(user_id=user_id)
            db.add(settings)
            db.commit()
            db.refresh(settings)
        
        return settings
    
    def update(self, db: Session, user_id: int, obj_in: NotificationSettingsUpdate) -> NotificationSettings:
        """更新通知设置"""
        settings = self.get_or_create(db, user_id)
        
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)
        
        settings.updated_at = datetime.utcnow()
        db.add(settings)
        db.commit()
        db.refresh(settings)
        return settings

class CRUDNotificationTemplate:
    """通知模板CRUD操作类"""
    
    def create(self, db: Session, obj_in: NotificationTemplateCreate) -> NotificationTemplate:
        """创建通知模板"""
        db_obj = NotificationTemplate(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[NotificationTemplate]:
        """获取通知模板"""
        return db.query(NotificationTemplate).filter(NotificationTemplate.id == id).first()
    
    def get_by_type(self, db: Session, type: NotificationType, is_active: bool = True) -> List[NotificationTemplate]:
        """根据类型获取通知模板"""
        query = db.query(NotificationTemplate).filter(NotificationTemplate.type == type)
        
        if is_active:
            query = query.filter(NotificationTemplate.is_active == True)
            
        return query.all()
    
    def get_all(self, db: Session, is_active: Optional[bool] = None) -> List[NotificationTemplate]:
        """获取所有通知模板"""
        query = db.query(NotificationTemplate)
        
        if is_active is not None:
            query = query.filter(NotificationTemplate.is_active == is_active)
            
        return query.order_by(NotificationTemplate.type, NotificationTemplate.name).all()

# 创建CRUD实例
notification = CRUDNotification()
notification_rule = CRUDNotificationRule()
notification_settings = CRUDNotificationSettings()
notification_template = CRUDNotificationTemplate()

