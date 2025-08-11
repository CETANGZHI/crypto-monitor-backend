from fastapi import APIRouter

router = APIRouter()

@router.get("/", summary="贝莱德持仓首页")
async def blackrock_home():
    """贝莱德持仓模块首页"""
    return {"message": "贝莱德持仓模块 - 开发中"}

@router.get("/holdings", summary="获取贝莱德持仓数据")
async def get_holdings():
    """获取贝莱德BTC/ETH持仓数据"""
    return {"message": "贝莱德持仓数据 - 开发中"}

