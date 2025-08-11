"""
Twitter服务模块
由于免费版Twitter API限制严格，暂时使用模拟数据
"""
import tweepy
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random
import logging

logger = logging.getLogger(__name__)

class TwitterService:
    """Twitter数据服务类"""
    
    def __init__(self, bearer_token: Optional[str] = None):
        """
        初始化Twitter服务
        
        Args:
            bearer_token: Twitter API Bearer Token（可选）
        """
        self.bearer_token = bearer_token
        self.client = None
        
        # 如果提供了token，尝试初始化真实API客户端
        if bearer_token:
            try:
                self.client = tweepy.Client(bearer_token=bearer_token)
                logger.info("Twitter API客户端初始化成功")
            except Exception as e:
                logger.warning(f"Twitter API客户端初始化失败: {e}")
                self.client = None
    
    def get_crypto_influencers_tweets(self, limit: int = 10) -> List[Dict]:
        """
        获取币圈大咖的推文
        
        Args:
            limit: 返回推文数量限制
            
        Returns:
            推文列表
        """
        # 由于免费版API限制，使用模拟数据
        return self._get_mock_tweets(limit)
    
    def get_user_tweets(self, username: str, limit: int = 5) -> List[Dict]:
        """
        获取指定用户的推文
        
        Args:
            username: 用户名
            limit: 返回推文数量限制
            
        Returns:
            推文列表
        """
        # 由于免费版API限制，使用模拟数据
        return self._get_mock_user_tweets(username, limit)
    
    def _get_mock_tweets(self, limit: int) -> List[Dict]:
        """
        生成模拟的币圈大咖推文数据
        
        Args:
            limit: 返回推文数量限制
            
        Returns:
            模拟推文列表
        """
        # 币圈大咖列表
        influencers = [
            {
                "username": "elonmusk",
                "display_name": "Elon Musk",
                "avatar": "https://pbs.twimg.com/profile_images/1683325380441128960/yRsRRjGO_400x400.jpg",
                "verified": True
            },
            {
                "username": "realDonaldTrump", 
                "display_name": "Donald J. Trump",
                "avatar": "https://pbs.twimg.com/profile_images/874276197357596672/kUuht00m_400x400.jpg",
                "verified": True
            },
            {
                "username": "justinsuntron",
                "display_name": "Justin Sun",
                "avatar": "https://pbs.twimg.com/profile_images/1345457748013142016/gCF5dKGF_400x400.jpg",
                "verified": True
            },
            {
                "username": "cz_binance",
                "display_name": "CZ Binance",
                "avatar": "https://pbs.twimg.com/profile_images/1493287503005511681/E_HjKI6E_400x400.jpg",
                "verified": True
            },
            {
                "username": "VitalikButerin",
                "display_name": "Vitalik Buterin",
                "avatar": "https://pbs.twimg.com/profile_images/977496875887558661/L86xyLF4_400x400.jpg",
                "verified": True
            }
        ]
        
        # 模拟推文内容模板
        tweet_templates = [
            "Bitcoin is the future of digital currency! 🚀 #BTC #Crypto",
            "Ethereum's latest upgrade is revolutionary for DeFi 💎 #ETH #DeFi",
            "The crypto market is showing strong bullish signals 📈 #Crypto",
            "Blockchain technology will transform the financial industry 🌐 #Blockchain",
            "HODL strong! The best is yet to come 💪 #HODL #Bitcoin",
            "DeFi protocols are changing how we think about finance 🔄 #DeFi",
            "NFTs represent a new era of digital ownership 🎨 #NFT",
            "Crypto adoption is accelerating worldwide 🌍 #Adoption",
            "Smart contracts are the backbone of Web3 ⚡ #SmartContracts",
            "The metaverse and crypto will merge beautifully 🎮 #Metaverse"
        ]
        
        tweets = []
        for i in range(limit):
            influencer = random.choice(influencers)
            tweet_content = random.choice(tweet_templates)
            
            # 生成随机时间（最近24小时内）
            hours_ago = random.randint(1, 24)
            created_at = datetime.now() - timedelta(hours=hours_ago)
            
            tweet = {
                "id": f"mock_tweet_{i}_{int(datetime.now().timestamp())}",
                "text": tweet_content,
                "author": {
                    "id": f"user_{influencer['username']}",
                    "username": influencer["username"],
                    "name": influencer["display_name"],
                    "profile_image_url": influencer["avatar"],
                    "verified": influencer["verified"]
                },
                "created_at": created_at.isoformat(),
                "public_metrics": {
                    "retweet_count": random.randint(100, 10000),
                    "like_count": random.randint(500, 50000),
                    "reply_count": random.randint(50, 5000),
                    "quote_count": random.randint(20, 2000)
                },
                "context_annotations": [
                    {
                        "domain": {"id": "65", "name": "Interests and Hobbies Vertical"},
                        "entity": {"id": "848920371311001600", "name": "Technology"}
                    }
                ],
                "lang": "en",
                "possibly_sensitive": False,
                "source": "Twitter for iPhone"
            }
            tweets.append(tweet)
        
        # 按时间倒序排列
        tweets.sort(key=lambda x: x["created_at"], reverse=True)
        return tweets
    
    def _get_mock_user_tweets(self, username: str, limit: int) -> List[Dict]:
        """
        生成指定用户的模拟推文数据
        
        Args:
            username: 用户名
            limit: 返回推文数量限制
            
        Returns:
            模拟推文列表
        """
        # 用户特定的推文内容
        user_specific_tweets = {
            "elonmusk": [
                "Dogecoin to the moon! 🐕🚀",
                "Tesla will accept Bitcoin payments soon",
                "Mars needs a cryptocurrency too 🔴",
                "X (formerly Twitter) + Crypto = Future",
                "Neuralink and blockchain integration coming"
            ],
            "realDonaldTrump": [
                "America needs to lead in cryptocurrency!",
                "Bitcoin is digital gold - tremendous!",
                "Crypto regulations should be fair and smart",
                "Make America's blockchain great again!",
                "The future of money is digital"
            ],
            "justinsuntron": [
                "TRON ecosystem is expanding rapidly! 🌟",
                "DeFi on TRON is the future",
                "Building the decentralized internet",
                "TRON's TPS is unmatched in the industry",
                "Partnerships driving TRON adoption"
            ],
            "cz_binance": [
                "Binance is committed to user security 🔒",
                "Building the infrastructure for Web3",
                "Crypto education is key to adoption",
                "Binance Smart Chain ecosystem growing",
                "Compliance and innovation go hand in hand"
            ],
            "VitalikButerin": [
                "Ethereum 2.0 progress update 📊",
                "Proof of Stake is more sustainable",
                "Layer 2 solutions scaling Ethereum",
                "DeFi innovation continues to amaze",
                "Ethereum's roadmap for the future"
            ]
        }
        
        # 获取用户特定内容，如果没有则使用通用内容
        tweet_contents = user_specific_tweets.get(username, [
            f"Latest update from {username}",
            f"Thoughts on the crypto market by {username}",
            f"{username}'s perspective on blockchain",
            f"Innovation insights from {username}",
            f"{username} shares market analysis"
        ])
        
        tweets = []
        for i in range(limit):
            content = random.choice(tweet_contents)
            hours_ago = random.randint(1, 72)  # 最近3天内
            created_at = datetime.now() - timedelta(hours=hours_ago)
            
            tweet = {
                "id": f"mock_{username}_{i}_{int(datetime.now().timestamp())}",
                "text": content,
                "author": {
                    "id": f"user_{username}",
                    "username": username,
                    "name": username.replace("_", " ").title(),
                    "profile_image_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}",
                    "verified": True
                },
                "created_at": created_at.isoformat(),
                "public_metrics": {
                    "retweet_count": random.randint(50, 5000),
                    "like_count": random.randint(200, 20000),
                    "reply_count": random.randint(20, 2000),
                    "quote_count": random.randint(10, 1000)
                },
                "lang": "en",
                "possibly_sensitive": False,
                "source": "Twitter Web App"
            }
            tweets.append(tweet)
        
        tweets.sort(key=lambda x: x["created_at"], reverse=True)
        return tweets
    
    def search_tweets(self, query: str, limit: int = 10) -> List[Dict]:
        """
        搜索推文（模拟实现）
        
        Args:
            query: 搜索关键词
            limit: 返回推文数量限制
            
        Returns:
            搜索结果推文列表
        """
        # 模拟搜索结果
        mock_tweets = self._get_mock_tweets(limit * 2)
        
        # 简单的关键词过滤
        filtered_tweets = []
        for tweet in mock_tweets:
            if query.lower() in tweet["text"].lower():
                filtered_tweets.append(tweet)
                if len(filtered_tweets) >= limit:
                    break
        
        # 如果过滤后结果不够，补充一些相关推文
        if len(filtered_tweets) < limit:
            remaining = limit - len(filtered_tweets)
            additional_tweets = self._generate_search_tweets(query, remaining)
            filtered_tweets.extend(additional_tweets)
        
        return filtered_tweets[:limit]
    
    def _generate_search_tweets(self, query: str, count: int) -> List[Dict]:
        """
        生成与搜索关键词相关的模拟推文
        
        Args:
            query: 搜索关键词
            count: 生成数量
            
        Returns:
            相关推文列表
        """
        tweets = []
        for i in range(count):
            hours_ago = random.randint(1, 48)
            created_at = datetime.now() - timedelta(hours=hours_ago)
            
            tweet = {
                "id": f"search_{query}_{i}_{int(datetime.now().timestamp())}",
                "text": f"Latest news about {query} in the crypto space! 📈 #{query} #Crypto",
                "author": {
                    "id": f"crypto_user_{i}",
                    "username": f"cryptouser{i}",
                    "name": f"Crypto User {i}",
                    "profile_image_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed=user{i}",
                    "verified": False
                },
                "created_at": created_at.isoformat(),
                "public_metrics": {
                    "retweet_count": random.randint(10, 1000),
                    "like_count": random.randint(50, 5000),
                    "reply_count": random.randint(5, 500),
                    "quote_count": random.randint(2, 200)
                },
                "lang": "en",
                "possibly_sensitive": False,
                "source": "Twitter for Android"
            }
            tweets.append(tweet)
        
        return tweets

# 全局Twitter服务实例
twitter_service = TwitterService()

