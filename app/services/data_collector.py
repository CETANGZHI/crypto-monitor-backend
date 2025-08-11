"""
多源数据采集器
整合RSS、第三方API、网页爬虫等多种数据源
"""
import asyncio
import aiohttp
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
from dataclasses import dataclass
import hashlib
import time
import random
from urllib.parse import urljoin, urlparse
import json

logger = logging.getLogger(__name__)

@dataclass
class InfluencerProfile:
    """影响者档案"""
    username: str
    display_name: str
    platform: str
    category: str  # 政界、科技界、交易所、项目方、金融圈
    importance_level: int  # 1-5，重要程度
    rss_url: Optional[str] = None
    twitter_id: Optional[str] = None
    description: str = ""
    avatar_url: str = ""
    verified: bool = False

class DataCollector:
    """多源数据采集器"""
    
    def __init__(self):
        self.influencers = self._init_influencers()
        self.session = None
        self.collected_posts = set()  # 用于去重
        
    def _init_influencers(self) -> List[InfluencerProfile]:
        """初始化影响者列表"""
        return [
            # 政界人士
            InfluencerProfile(
                username="realDonaldTrump",
                display_name="Donald J. Trump",
                platform="twitter",
                category="政界",
                importance_level=5,
                description="美国前总统，对加密货币政策有重大影响",
                verified=True
            ),
            
            # 科技界大咖
            InfluencerProfile(
                username="elonmusk",
                display_name="Elon Musk",
                platform="twitter",
                category="科技界",
                importance_level=5,
                description="特斯拉CEO，SpaceX创始人，加密货币影响者",
                verified=True
            ),
            InfluencerProfile(
                username="VitalikButerin",
                display_name="Vitalik Buterin",
                platform="twitter",
                category="科技界",
                importance_level=5,
                description="以太坊创始人",
                verified=True
            ),
            
            # 交易所高管
            InfluencerProfile(
                username="cz_binance",
                display_name="Changpeng Zhao (CZ)",
                platform="twitter",
                category="交易所",
                importance_level=5,
                description="Binance创始人兼CEO",
                verified=True
            ),
            InfluencerProfile(
                username="brian_armstrong",
                display_name="Brian Armstrong",
                platform="twitter",
                category="交易所",
                importance_level=4,
                description="Coinbase CEO",
                verified=True
            ),
            
            # 项目方创始人
            InfluencerProfile(
                username="justinsuntron",
                display_name="Justin Sun",
                platform="twitter",
                category="项目方",
                importance_level=4,
                description="TRON创始人",
                verified=True
            ),
            InfluencerProfile(
                username="stablekwon",
                display_name="Do Kwon",
                platform="twitter",
                category="项目方",
                importance_level=3,
                description="Terra创始人（已倒闭）",
                verified=False
            ),
            
            # 金融圈人士
            InfluencerProfile(
                username="saylor",
                display_name="Michael Saylor",
                platform="twitter",
                category="金融圈",
                importance_level=5,
                description="MicroStrategy CEO，比特币支持者",
                verified=True
            ),
            InfluencerProfile(
                username="APompliano",
                display_name="Anthony Pompliano",
                platform="twitter",
                category="金融圈",
                importance_level=4,
                description="投资者，加密货币倡导者",
                verified=True
            ),
            InfluencerProfile(
                username="CathieDWood",
                display_name="Cathie Wood",
                platform="twitter",
                category="金融圈",
                importance_level=4,
                description="ARK Invest CEO",
                verified=True
            ),
        ]
    
    async def collect_all_data(self) -> List[Dict]:
        """采集所有数据源的数据"""
        all_posts = []
        
        # 并行采集各种数据源
        tasks = [
            self.collect_rss_data(),
            self.collect_mock_api_data(),
            self.collect_public_data(),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"数据采集错误: {result}")
            elif isinstance(result, list):
                all_posts.extend(result)
        
        # 去重和排序
        unique_posts = self._deduplicate_posts(all_posts)
        sorted_posts = sorted(unique_posts, key=lambda x: x.get('created_at', ''), reverse=True)
        
        logger.info(f"成功采集 {len(sorted_posts)} 条数据")
        return sorted_posts
    
    async def collect_rss_data(self) -> List[Dict]:
        """采集RSS数据"""
        posts = []
        
        # RSS源列表（一些可能的RSS源）
        rss_sources = [
            {
                "url": "https://rss.cnn.com/rss/money_news_international.rss",
                "category": "财经新闻",
                "source": "CNN"
            },
            {
                "url": "https://feeds.bloomberg.com/markets/news.rss",
                "category": "市场新闻", 
                "source": "Bloomberg"
            },
            # 注意：实际的推特RSS源需要特殊服务
        ]
        
        for source in rss_sources:
            try:
                feed = feedparser.parse(source["url"])
                for entry in feed.entries[:5]:  # 限制每个源最多5条
                    post = {
                        "id": self._generate_post_id(entry.link),
                        "text": entry.title + " " + getattr(entry, 'summary', ''),
                        "author": {
                            "username": source["source"].lower(),
                            "name": source["source"],
                            "verified": True,
                            "category": source["category"]
                        },
                        "created_at": self._parse_date(getattr(entry, 'published', '')),
                        "source": "RSS",
                        "url": entry.link,
                        "engagement": {
                            "likes": random.randint(10, 1000),
                            "shares": random.randint(5, 500),
                            "comments": random.randint(2, 200)
                        }
                    }
                    posts.append(post)
                    
            except Exception as e:
                logger.error(f"RSS采集错误 {source['url']}: {e}")
        
        return posts
    
    async def collect_mock_api_data(self) -> List[Dict]:
        """模拟第三方API数据采集"""
        posts = []
        
        # 模拟从第三方API获取的数据
        for influencer in self.influencers:
            try:
                # 模拟API调用延迟
                await asyncio.sleep(0.1)
                
                # 生成该影响者的模拟推文
                influencer_posts = self._generate_influencer_posts(influencer)
                posts.extend(influencer_posts)
                
            except Exception as e:
                logger.error(f"API采集错误 {influencer.username}: {e}")
        
        return posts
    
    async def collect_public_data(self) -> List[Dict]:
        """采集公开数据源"""
        posts = []
        
        # 模拟从公开数据源采集
        public_sources = [
            {
                "name": "CoinDesk",
                "category": "加密新闻",
                "posts": [
                    "Bitcoin reaches new all-time high amid institutional adoption",
                    "Ethereum 2.0 staking rewards attract more validators",
                    "DeFi protocols see record TVL growth this quarter"
                ]
            },
            {
                "name": "CoinTelegraph", 
                "category": "区块链新闻",
                "posts": [
                    "Major bank announces crypto custody services",
                    "NFT marketplace launches new creator tools",
                    "Central bank digital currency pilot program expands"
                ]
            }
        ]
        
        for source in public_sources:
            for i, post_text in enumerate(source["posts"]):
                post = {
                    "id": self._generate_post_id(f"{source['name']}_{i}_{int(time.time())}"),
                    "text": post_text,
                    "author": {
                        "username": source["name"].lower().replace(" ", ""),
                        "name": source["name"],
                        "verified": True,
                        "category": source["category"]
                    },
                    "created_at": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
                    "source": "公开数据",
                    "engagement": {
                        "likes": random.randint(100, 5000),
                        "shares": random.randint(50, 2000),
                        "comments": random.randint(20, 1000)
                    }
                }
                posts.append(post)
        
        return posts
    
    def _generate_influencer_posts(self, influencer: InfluencerProfile) -> List[Dict]:
        """为特定影响者生成模拟推文"""
        posts = []
        
        # 根据影响者类别生成相关内容
        content_templates = {
            "政界": [
                "America needs strong cryptocurrency regulations that protect innovation",
                "Digital assets represent the future of American financial leadership",
                "Blockchain technology will revolutionize government transparency"
            ],
            "科技界": [
                "The future of money is digital and decentralized",
                "Blockchain technology is reshaping how we think about trust",
                "Cryptocurrency adoption is accelerating faster than expected"
            ],
            "交易所": [
                "Building the infrastructure for the future of finance",
                "Security and compliance remain our top priorities",
                "Expanding access to digital assets globally"
            ],
            "项目方": [
                "Our ecosystem continues to grow with new partnerships",
                "Innovation in DeFi is driving the next wave of adoption",
                "Community governance is the future of decentralized protocols"
            ],
            "金融圈": [
                "Bitcoin is digital gold for the 21st century",
                "Institutional adoption of crypto is just beginning",
                "Portfolio diversification should include digital assets"
            ]
        }
        
        templates = content_templates.get(influencer.category, content_templates["科技界"])
        
        # 生成1-3条推文
        num_posts = random.randint(1, 3)
        for i in range(num_posts):
            hours_ago = random.randint(1, 48)
            created_at = datetime.now() - timedelta(hours=hours_ago)
            
            post = {
                "id": self._generate_post_id(f"{influencer.username}_{i}_{int(time.time())}"),
                "text": random.choice(templates),
                "author": {
                    "username": influencer.username,
                    "name": influencer.display_name,
                    "verified": influencer.verified,
                    "category": influencer.category,
                    "importance_level": influencer.importance_level
                },
                "created_at": created_at.isoformat(),
                "source": "第三方API",
                "platform": influencer.platform,
                "engagement": {
                    "likes": random.randint(1000, 50000) * influencer.importance_level,
                    "shares": random.randint(100, 10000) * influencer.importance_level,
                    "comments": random.randint(50, 5000) * influencer.importance_level
                }
            }
            posts.append(post)
        
        return posts
    
    def _generate_post_id(self, content: str) -> str:
        """生成唯一的帖子ID"""
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _parse_date(self, date_str: str) -> str:
        """解析日期字符串"""
        if not date_str:
            return datetime.now().isoformat()
        
        try:
            # 尝试解析常见的日期格式
            import dateutil.parser
            parsed_date = dateutil.parser.parse(date_str)
            return parsed_date.isoformat()
        except:
            return datetime.now().isoformat()
    
    def _deduplicate_posts(self, posts: List[Dict]) -> List[Dict]:
        """去重帖子"""
        seen_ids = set()
        unique_posts = []
        
        for post in posts:
            post_id = post.get('id')
            if post_id and post_id not in seen_ids:
                seen_ids.add(post_id)
                unique_posts.append(post)
        
        return unique_posts
    
    async def get_influencer_stats(self) -> Dict:
        """获取影响者统计信息"""
        stats = {
            "total_influencers": len(self.influencers),
            "by_category": {},
            "by_importance": {},
            "top_influencers": []
        }
        
        # 按类别统计
        for influencer in self.influencers:
            category = influencer.category
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
        
        # 按重要程度统计
        for influencer in self.influencers:
            level = influencer.importance_level
            stats["by_importance"][f"level_{level}"] = stats["by_importance"].get(f"level_{level}", 0) + 1
        
        # 顶级影响者
        top_influencers = sorted(self.influencers, key=lambda x: x.importance_level, reverse=True)[:5]
        stats["top_influencers"] = [
            {
                "username": inf.username,
                "name": inf.display_name,
                "category": inf.category,
                "importance": inf.importance_level
            }
            for inf in top_influencers
        ]
        
        return stats

class RSSCollector:
    """RSS数据采集器"""
    
    def __init__(self):
        self.rss_sources = [
            # 加密货币新闻RSS源
            "https://cointelegraph.com/rss",
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "https://decrypt.co/feed",
            # 财经新闻RSS源
            "https://feeds.bloomberg.com/markets/news.rss",
            "https://www.reuters.com/rssFeed/businessNews",
        ]
    
    async def collect_news(self, limit: int = 20) -> List[Dict]:
        """采集新闻数据"""
        all_news = []
        
        for rss_url in self.rss_sources:
            try:
                feed = feedparser.parse(rss_url)
                source_name = urlparse(rss_url).netloc
                
                for entry in feed.entries[:5]:  # 每个源最多5条
                    news_item = {
                        "id": self._generate_id(entry.link),
                        "title": entry.title,
                        "summary": getattr(entry, 'summary', ''),
                        "url": entry.link,
                        "source": source_name,
                        "published": self._parse_date(getattr(entry, 'published', '')),
                        "category": "crypto_news"
                    }
                    all_news.append(news_item)
                    
            except Exception as e:
                logger.error(f"RSS采集错误 {rss_url}: {e}")
        
        # 按发布时间排序
        all_news.sort(key=lambda x: x['published'], reverse=True)
        return all_news[:limit]
    
    def _generate_id(self, url: str) -> str:
        """生成新闻ID"""
        return hashlib.md5(url.encode()).hexdigest()[:16]
    
    def _parse_date(self, date_str: str) -> str:
        """解析日期"""
        if not date_str:
            return datetime.now().isoformat()
        
        try:
            import dateutil.parser
            parsed_date = dateutil.parser.parse(date_str)
            return parsed_date.isoformat()
        except:
            return datetime.now().isoformat()

# 全局数据采集器实例
data_collector = DataCollector()
rss_collector = RSSCollector()

