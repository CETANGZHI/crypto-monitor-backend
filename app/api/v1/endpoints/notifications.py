from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.crud.crud_notification import notification, notification_rule, notification_settings
from app import schemas
from app.api import deps
from app.models.user import User
from app.models.notification import NotificationType, NotificationStatus

router = APIRouter()

# 通知相关API
@router.get("/", summary="通知管理首页")
async def notifications_home():
    """通知管理首页"""
    return {
        "message": "通知管理系统",
        "features": [
            "实时通知推送",
            "通知规则配置",
            "通知设置管理",
            "通知统计分析"
        ]
    }

@router.get("/list", response_model=schemas.NotificationList, summary="获取通知列表")
async def get_notifications(
    status: Optional[NotificationStatus] = Query(None, description="通知状态筛选"),
    type: Optional[NotificationType] = Query(None, description="通知类型筛选"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    获取当前用户的通知列表
    
    - **status**: 通知状态筛选 (unread, read, archived)
    - **type**: 通知类型筛选 (twitter, wallet, blackrock, system)
    - **skip**: 跳过数量
    - **limit**: 返回数量
    """
    notifications = notification.get_by_user(
        db, 
        user_id=current_user.id, 
        status=status, 
        type=type, 
        skip=skip, 
        limit=limit
    )
    
    total = len(notifications)  # 简化实现，实际应该查询总数
    unread_count = notification.get_unread_count(db, user_id=current_user.id)
    
    return schemas.NotificationList(
        notifications=notifications,
        total=total,
        unread_count=unread_count
    )

@router.get("/stats", response_model=schemas.NotificationStats, summary="获取通知统计")
async def get_notification_stats(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """获取当前用户的通知统计信息"""
    stats = notification.get_stats(db, user_id=current_user.id)
    
    # 获取最近的通知
    recent_notifications = notification.get_by_user(
        db, 
        user_id=current_user.id, 
        skip=0, 
        limit=5
    )
    
    stats["recent_notifications"] = recent_notifications
    return stats

@router.put("/{notification_id}/read", response_model=schemas.NotificationResponse, summary="标记通知为已读")
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """标记指定通知为已读"""
    updated_notification = notification.mark_as_read(
        db, 
        notification_id=notification_id, 
        user_id=current_user.id
    )
    
    if not updated_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    return updated_notification

@router.put("/read-all", summary="标记所有通知为已读")
async def mark_all_notifications_as_read(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """标记当前用户所有通知为已读"""
    count = notification.mark_all_as_read(db, user_id=current_user.id)
    
    return {
        "message": f"已标记 {count} 条通知为已读",
        "count": count
    }

@router.put("/batch-update", summary="批量更新通知状态")
async def batch_update_notifications(
    batch_update: schemas.NotificationBatchUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """批量更新通知状态"""
    count = notification.batch_update_status(
        db,
        notification_ids=batch_update.notification_ids,
        user_id=current_user.id,
        status=batch_update.status
    )
    
    return {
        "message": f"已更新 {count} 条通知状态",
        "count": count
    }

@router.delete("/{notification_id}", summary="删除通知")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """删除指定通知"""
    success = notification.delete(
        db, 
        id=notification_id, 
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    return {"message": "通知已删除"}

# 通知规则相关API
@router.get("/rules", response_model=List[schemas.NotificationRuleResponse], summary="获取通知规则列表")
async def get_notification_rules(
    is_active: Optional[bool] = Query(None, description="是否激活"),
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """获取当前用户的通知规则列表"""
    rules = notification_rule.get_by_user(
        db, 
        user_id=current_user.id, 
        is_active=is_active
    )
    return rules

@router.post("/rules", response_model=schemas.NotificationRuleResponse, summary="创建通知规则")
async def create_notification_rule(
    rule_in: schemas.NotificationRuleCreate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """创建新的通知规则"""
    rule = notification_rule.create(
        db, 
        obj_in=rule_in, 
        user_id=current_user.id
    )
    return rule

@router.get("/rules/{rule_id}", response_model=schemas.NotificationRuleResponse, summary="获取通知规则详情")
async def get_notification_rule(
    rule_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """获取指定通知规则的详情"""
    rule = notification_rule.get(
        db, 
        id=rule_id, 
        user_id=current_user.id
    )
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知规则不存在"
        )
    
    return rule

@router.put("/rules/{rule_id}", response_model=schemas.NotificationRuleResponse, summary="更新通知规则")
async def update_notification_rule(
    rule_id: int,
    rule_update: schemas.NotificationRuleUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """更新指定的通知规则"""
    rule = notification_rule.get(
        db, 
        id=rule_id, 
        user_id=current_user.id
    )
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知规则不存在"
        )
    
    updated_rule = notification_rule.update(
        db, 
        db_obj=rule, 
        obj_in=rule_update
    )
    return updated_rule

@router.delete("/rules/{rule_id}", summary="删除通知规则")
async def delete_notification_rule(
    rule_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """删除指定的通知规则"""
    success = notification_rule.delete(
        db, 
        id=rule_id, 
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知规则不存在"
        )
    
    return {"message": "通知规则已删除"}

# 通知设置相关API
@router.get("/settings", response_model=schemas.NotificationSettingsResponse, summary="获取通知设置")
async def get_notification_settings(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """获取当前用户的通知设置"""
    settings = notification_settings.get_or_create(
        db, 
        user_id=current_user.id
    )
    return settings

@router.put("/settings", response_model=schemas.NotificationSettingsResponse, summary="更新通知设置")
async def update_notification_settings(
    settings_update: schemas.NotificationSettingsUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """更新当前用户的通知设置"""
    updated_settings = notification_settings.update(
        db, 
        user_id=current_user.id, 
        obj_in=settings_update
    )
    return updated_settings

