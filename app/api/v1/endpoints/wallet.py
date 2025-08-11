from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ....services.blockchain_service import blockchain_service
from ....services.twitter_wallet_service import twitter_wallet_service
from ....schemas.user import UserResponse
from ....api.deps import get_current_user

router = APIRouter()

@router.get("/list")
async def get_wallet_list(
    current_user: UserResponse = Depends(get_current_user)
):
    """获取用户监控的钱包列表"""
    try:
        # 这里应该从数据库获取用户的钱包列表
        # 目前返回模拟数据
        wallets = [
            {
                "id": "1",
                "address": "0x742d35Cc6634C0532925a3b8D4C2F2b4C2F2b4C2",
                "label": "马斯克钱包",
                "is_active": True,
                "currentValue": 2450000,
                "change24h": 12.5,
                "lastActivity": "2024-01-15T10:30:00Z"
            },
            {
                "id": "2", 
                "address": "0x8ba1f109551bD432803012645Hac136c22C2F2b4",
                "label": "孙宇晨钱包",
                "is_active": True,
                "currentValue": 1850000,
                "change24h": -8.2,
                "lastActivity": "2024-01-15T09:15:00Z"
            }
        ]
        
        return {
            "success": True,
            "data": wallets,
            "message": "钱包列表获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取钱包列表失败: {str(e)}")

@router.post("/add")
async def add_wallet(
    address: str,
    label: str = "未命名钱包",
    current_user: UserResponse = Depends(get_current_user)
):
    """添加钱包地址到监控列表"""
    try:
        # 验证钱包地址格式
        if not address.startswith('0x') or len(address) != 42:
            raise HTTPException(status_code=400, detail="无效的钱包地址格式")
        
        # 获取钱包基本信息
        wallet_data = await blockchain_service.get_wallet_balance(address)
        
        # 这里应该保存到数据库
        new_wallet = {
            "id": "new_wallet_id",
            "address": address,
            "label": label,
            "is_active": True,
            "currentValue": wallet_data.get('total_value_usd', 0),
            "change24h": 0,
            "lastActivity": wallet_data.get('last_updated'),
            "created_at": wallet_data.get('last_updated')
        }
        
        return {
            "success": True,
            "data": new_wallet,
            "message": "钱包添加成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加钱包失败: {str(e)}")

@router.get("/{wallet_id}/balance")
async def get_wallet_balance(
    wallet_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """获取钱包余额信息"""
    try:
        # 这里应该从数据库获取钱包地址
        # 目前使用模拟地址
        address = "0x742d35Cc6634C0532925a3b8D4C2F2b4C2F2b4C2"
        
        balance_data = await blockchain_service.get_wallet_balance(address)
        
        return {
            "success": True,
            "data": balance_data,
            "message": "余额信息获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取余额失败: {str(e)}")

@router.get("/{wallet_id}/transactions")
async def get_wallet_transactions(
    wallet_id: str,
    limit: int = Query(50, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取钱包交易记录"""
    try:
        # 这里应该从数据库获取钱包地址
        address = "0x742d35Cc6634C0532925a3b8D4C2F2b4C2F2b4C2"
        
        transactions = await blockchain_service.get_wallet_transactions(address, limit)
        
        return {
            "success": True,
            "data": transactions,
            "message": "交易记录获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易记录失败: {str(e)}")

@router.get("/{wallet_id}/holdings")
async def get_wallet_holdings(
    wallet_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """获取钱包持仓信息"""
    try:
        # 这里应该从数据库获取钱包地址
        address = "0x742d35Cc6634C0532925a3b8D4C2F2b4C2F2b4C2"
        
        holdings = await blockchain_service.get_wallet_holdings(address)
        
        return {
            "success": True,
            "data": holdings,
            "message": "持仓信息获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取持仓信息失败: {str(e)}")

@router.get("/{wallet_id}/activity")
async def get_wallet_activity(
    wallet_id: str,
    days: int = Query(30, ge=1, le=365),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取钱包活动分析"""
    try:
        # 这里应该从数据库获取钱包地址
        address = "0x742d35Cc6634C0532925a3b8D4C2F2b4C2F2b4C2"
        
        activity = await blockchain_service.analyze_wallet_activity(address, days)
        
        return {
            "success": True,
            "data": activity,
            "message": "活动分析获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取活动分析失败: {str(e)}")

@router.patch("/{wallet_id}")
async def update_wallet(
    wallet_id: str,
    is_active: Optional[bool] = None,
    label: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """更新钱包设置"""
    try:
        # 这里应该更新数据库中的钱包信息
        updated_wallet = {
            "id": wallet_id,
            "is_active": is_active,
            "label": label,
            "updated_at": "2024-01-15T10:30:00Z"
        }
        
        return {
            "success": True,
            "data": updated_wallet,
            "message": "钱包更新成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新钱包失败: {str(e)}")

@router.delete("/{wallet_id}")
async def delete_wallet(
    wallet_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """删除钱包"""
    try:
        # 这里应该从数据库删除钱包
        return {
            "success": True,
            "message": "钱包删除成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除钱包失败: {str(e)}")

# 新增：推特用户钱包关联API
@router.get("/twitter/{username}")
async def get_twitter_user_wallets(
    username: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """获取推特用户关联的钱包地址"""
    try:
        user_wallets = await twitter_wallet_service.get_user_wallets(username)
        
        return {
            "success": True,
            "data": user_wallets,
            "message": f"获取 @{username} 的钱包信息成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取推特用户钱包失败: {str(e)}")

@router.get("/twitter/{username}/portfolio")
async def get_twitter_user_portfolio(
    username: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """获取推特用户的投资组合摘要"""
    try:
        portfolio = await twitter_wallet_service.get_user_portfolio_summary(username)
        
        return {
            "success": True,
            "data": portfolio,
            "message": f"获取 @{username} 的投资组合成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取投资组合失败: {str(e)}")

@router.get("/twitter/{username}/connections")
async def get_twitter_user_wallet_connections(
    username: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """分析推特用户钱包之间的关联性"""
    try:
        connections = await twitter_wallet_service.analyze_wallet_connections(username)
        
        return {
            "success": True,
            "data": connections,
            "message": f"获取 @{username} 的钱包关联分析成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析钱包关联失败: {str(e)}")

@router.get("/transactions")
async def get_all_transactions(
    limit: int = Query(50, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取所有监控钱包的交易记录"""
    try:
        # 这里应该获取用户所有钱包的交易记录
        # 目前返回模拟数据
        transactions = [
            {
                "id": "1",
                "type": "out",
                "amount": "500",
                "token": "BTC",
                "value": 21500000,
                "counterparty": "0x1234567890abcdef1234567890abcdef12345678",
                "timestamp": "2024-01-15T10:30:00Z"
            },
            {
                "id": "2",
                "type": "in", 
                "amount": "1000",
                "token": "ETH",
                "value": 2400000,
                "counterparty": "0xabcdef1234567890abcdef1234567890abcdef12",
                "timestamp": "2024-01-15T09:15:00Z"
            }
        ]
        
        return {
            "success": True,
            "data": transactions,
            "message": "交易记录获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易记录失败: {str(e)}")

# 保留原有的端点以保持兼容性
@router.get("/", summary="钱包监控首页")
async def wallet_home():
    """钱包监控模块首页"""
    return {"message": "钱包监控模块 - 已升级"}

@router.get("/addresses", summary="获取预设钱包地址列表")
async def get_preset_addresses():
    """获取系统预设的钱包地址列表"""
    return {"message": "钱包地址列表 - 已升级"}

