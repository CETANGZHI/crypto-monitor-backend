"""
推特监控API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import asyncio
from app.services.data_collector import data_collector, rss_collector
from app.services.twitter_service import twitter_service

router = APIRouter()

@router.get("/", summary="推特监控首页")
async def twitter_home():
    """推特监控首页"""
    return {
        "message": "推特监控服务",
        "description": "监控币圈大咖的推特动态",
        "features": [
            "多源数据采集",
            "实时推文监控", 
            "影响者分析",
            "趋势追踪"
        ]
    }

@router.get("/influencers", summary="获取影响者统计")
async def get_influencers():
    """获取影响者列表和统计信息"""
    try:
        stats = await data_collector.get_influencer_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取影响者信息失败: {str(e)}")

@router.get("/posts", summary="获取最新推文")
async def get_latest_posts(
    limit: int = Query(default=20, ge=1, le=100, description="返回帖子数量"),
    category: Optional[str] = Query(default=None, description="影响者类别筛选")
):
    """获取最新的推文和帖子"""
    try:
        # 采集所有数据源的数据
        all_posts = await data_collector.collect_all_data()
        
        # 如果指定了类别，进行筛选
        if category:
            filtered_posts = [
                post for post in all_posts 
                if post.get('author', {}).get('category') == category
            ]
            all_posts = filtered_posts
        
        # 限制返回数量
        limited_posts = all_posts[:limit]
        
        return {
            "success": True,
            "data": {
                "posts": limited_posts,
                "total": len(limited_posts),
                "categories": list(set(post.get('author', {}).get('category', 'unknown') for post in all_posts))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取推文失败: {str(e)}")

@router.get("/user/{username}", summary="获取用户推文")
async def get_user_posts(
    username: str,
    limit: int = Query(default=10, ge=1, le=50, description="返回帖子数量")
):
    """获取指定用户的推文"""
    try:
        # 使用Twitter服务获取用户推文
        user_posts = twitter_service.get_user_tweets(username, limit)
        
        return {
            "success": True,
            "data": {
                "username": username,
                "posts": user_posts,
                "total": len(user_posts)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户推文失败: {str(e)}")

@router.get("/news", summary="获取加密货币新闻")
async def get_crypto_news(
    limit: int = Query(default=15, ge=1, le=50, description="返回新闻数量")
):
    """获取加密货币相关新闻"""
    try:
        news = await rss_collector.collect_news(limit)
        
        return {
            "success": True,
            "data": {
                "news": news,
                "total": len(news),
                "sources": list(set(item['source'] for item in news))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取新闻失败: {str(e)}")

@router.get("/trending", summary="获取趋势话题")
async def get_trending_topics():
    """获取趋势话题"""
    try:
        # 模拟趋势话题数据
        trending_topics = [
            {
                "topic": "#Bitcoin",
                "posts_count": 15420,
                "sentiment": "bullish",
                "change_24h": "+12.5%"
            },
            {
                "topic": "#Ethereum",
                "posts_count": 8930,
                "sentiment": "bullish", 
                "change_24h": "+8.2%"
            },
            {
                "topic": "#DeFi",
                "posts_count": 5670,
                "sentiment": "neutral",
                "change_24h": "+2.1%"
            },
            {
                "topic": "#NFT",
                "posts_count": 4320,
                "sentiment": "bearish",
                "change_24h": "-5.3%"
            },
            {
                "topic": "#Web3",
                "posts_count": 3890,
                "sentiment": "bullish",
                "change_24h": "+15.7%"
            }
        ]
        
        return {
            "success": True,
            "data": {
                "trending": trending_topics,
                "updated_at": "2025-08-11T15:30:00Z"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取趋势话题失败: {str(e)}")

@router.get("/search", summary="搜索推文")
async def search_posts(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(default=10, ge=1, le=50, description="返回结果数量")
):
    """搜索推文和帖子"""
    try:
        # 使用Twitter服务搜索
        search_results = twitter_service.search_tweets(q, limit)
        
        return {
            "success": True,
            "data": {
                "query": q,
                "results": search_results,
                "total": len(search_results)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.get("/accounts", summary="获取预设推特账号列表")
async def get_preset_accounts():
    """获取预设推特账号列表"""
    try:
        # 从数据采集器获取影响者列表
        stats = await data_collector.get_influencer_stats()
        
        preset_accounts = [
            {
                "username": "elonmusk",
                "display_name": "Elon Musk",
                "category": "科技界",
                "followers": "150M+",
                "description": "特斯拉CEO，SpaceX创始人",
                "importance": 5,
                "verified": True
            },
            {
                "username": "realDonaldTrump", 
                "display_name": "Donald J. Trump",
                "category": "政界",
                "followers": "80M+",
                "description": "美国前总统",
                "importance": 5,
                "verified": True
            },
            {
                "username": "cz_binance",
                "display_name": "Changpeng Zhao",
                "category": "交易所",
                "followers": "8M+", 
                "description": "Binance创始人",
                "importance": 5,
                "verified": True
            },
            {
                "username": "VitalikButerin",
                "display_name": "Vitalik Buterin", 
                "category": "科技界",
                "followers": "5M+",
                "description": "以太坊创始人",
                "importance": 5,
                "verified": True
            },
            {
                "username": "saylor",
                "display_name": "Michael Saylor",
                "category": "金融圈",
                "followers": "3M+",
                "description": "MicroStrategy CEO",
                "importance": 5,
                "verified": True
            }
        ]
        
        return {
            "success": True,
            "data": {
                "accounts": preset_accounts,
                "total": len(preset_accounts),
                "stats": stats
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取账号列表失败: {str(e)}")

