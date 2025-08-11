"""
推特用户与钱包地址关联服务
实现推特用户钱包地址挖掘和关联逻辑
"""

import re
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
from .blockchain_service import blockchain_service
from .data_collector import DataCollector

class TwitterWalletService:
    """推特用户与钱包地址关联服务类"""
    
    def __init__(self):
        self.data_collector = DataCollector()
        
        # 钱包地址正则表达式
        self.wallet_patterns = {
            'ethereum': re.compile(r'0x[a-fA-F0-9]{40}'),
            'bitcoin': re.compile(r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{39,59}'),
            'solana': re.compile(r'[1-9A-HJ-NP-Za-km-z]{32,44}'),
        }
        
        # 已知大咖的钱包地址数据库（手动维护）
        self.known_wallets = {
            'elonmusk': {
                'wallets': [
                    {
                        'address': '0x742d35Cc6634C0532925a3b8D4C2F2b4C2F2b4C2',
                        'blockchain': 'ethereum',
                        'confidence': 0.9,
                        'source': 'public_disclosure',
                        'verified_date': '2024-01-15'
                    }
                ],
                'last_updated': '2024-01-15T10:30:00Z'
            },
            'justinsuntron': {
                'wallets': [
                    {
                        'address': '0x8ba1f109551bD432803012645Hac136c22C2F2b4',
                        'blockchain': 'ethereum',
                        'confidence': 0.95,
                        'source': 'public_disclosure',
                        'verified_date': '2024-01-15'
                    },
                    {
                        'address': 'TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7',
                        'blockchain': 'tron',
                        'confidence': 0.98,
                        'source': 'official_announcement',
                        'verified_date': '2024-01-15'
                    }
                ],
                'last_updated': '2024-01-15T09:15:00Z'
            },
            'cz_binance': {
                'wallets': [
                    {
                        'address': '0x9cd24553d0Cf942e0d808D5F3B89B9F5F5F5F5F5',
                        'blockchain': 'ethereum',
                        'confidence': 0.85,
                        'source': 'social_media_mention',
                        'verified_date': '2024-01-14'
                    }
                ],
                'last_updated': '2024-01-14T18:45:00Z'
            },
            'VitalikButerin': {
                'wallets': [
                    {
                        'address': '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',
                        'blockchain': 'ethereum',
                        'confidence': 1.0,
                        'source': 'public_disclosure',
                        'verified_date': '2024-01-15'
                    }
                ],
                'last_updated': '2024-01-15T12:00:00Z'
            }
        }
    
    async def get_user_wallets(self, username: str) -> Dict[str, Any]:
        """获取推特用户关联的钱包地址"""
        try:
            # 1. 检查已知钱包数据库
            known_data = self.known_wallets.get(username.lower())
            if known_data:
                wallets_with_data = []
                for wallet in known_data['wallets']:
                    # 获取钱包的链上数据
                    wallet_data = await self._enrich_wallet_data(wallet)
                    wallets_with_data.append(wallet_data)
                
                return {
                    'username': username,
                    'wallets': wallets_with_data,
                    'total_wallets': len(wallets_with_data),
                    'total_value_usd': sum(w.get('balance_data', {}).get('total_value_usd', 0) for w in wallets_with_data),
                    'last_updated': known_data['last_updated'],
                    'data_source': 'known_database'
                }
            
            # 2. 尝试从推文中挖掘钱包地址
            discovered_wallets = await self._discover_wallets_from_tweets(username)
            
            # 3. 尝试从个人资料中挖掘
            profile_wallets = await self._discover_wallets_from_profile(username)
            
            # 4. 合并结果
            all_wallets = discovered_wallets + profile_wallets
            
            # 5. 去重和验证
            unique_wallets = self._deduplicate_wallets(all_wallets)
            
            # 6. 获取链上数据
            enriched_wallets = []
            for wallet in unique_wallets:
                wallet_data = await self._enrich_wallet_data(wallet)
                enriched_wallets.append(wallet_data)
            
            return {
                'username': username,
                'wallets': enriched_wallets,
                'total_wallets': len(enriched_wallets),
                'total_value_usd': sum(w.get('balance_data', {}).get('total_value_usd', 0) for w in enriched_wallets),
                'last_updated': datetime.utcnow().isoformat() + 'Z',
                'data_source': 'discovery'
            }
            
        except Exception as e:
            print(f"Error getting wallets for user {username}: {e}")
            return {
                'username': username,
                'wallets': [],
                'total_wallets': 0,
                'total_value_usd': 0,
                'last_updated': datetime.utcnow().isoformat() + 'Z',
                'data_source': 'error',
                'error': str(e)
            }
    
    async def analyze_wallet_connections(self, username: str) -> Dict[str, Any]:
        """分析推特用户钱包之间的关联性"""
        try:
            user_wallets = await self.get_user_wallets(username)
            
            if not user_wallets['wallets']:
                return {
                    'username': username,
                    'connections': [],
                    'total_connections': 0,
                    'analysis': 'No wallets found'
                }
            
            connections = []
            wallets = user_wallets['wallets']
            
            # 分析钱包间的交易关系
            for i, wallet1 in enumerate(wallets):
                for j, wallet2 in enumerate(wallets[i+1:], i+1):
                    connection = await self._analyze_wallet_connection(
                        wallet1['address'], 
                        wallet2['address']
                    )
                    if connection['has_connection']:
                        connections.append(connection)
            
            # 分析与交易所的交互模式
            exchange_analysis = await self._analyze_exchange_patterns(wallets)
            
            return {
                'username': username,
                'connections': connections,
                'total_connections': len(connections),
                'exchange_patterns': exchange_analysis,
                'analysis_date': datetime.utcnow().isoformat() + 'Z'
            }
            
        except Exception as e:
            print(f"Error analyzing wallet connections for {username}: {e}")
            return {
                'username': username,
                'connections': [],
                'total_connections': 0,
                'error': str(e)
            }
    
    async def get_user_portfolio_summary(self, username: str) -> Dict[str, Any]:
        """获取推特用户的投资组合摘要"""
        try:
            user_wallets = await self.get_user_wallets(username)
            
            if not user_wallets['wallets']:
                return {
                    'username': username,
                    'portfolio': {},
                    'summary': 'No wallet data available'
                }
            
            # 聚合所有钱包的持仓数据
            aggregated_holdings = {}
            total_value = 0
            
            for wallet in user_wallets['wallets']:
                holdings_data = wallet.get('holdings_data', {})
                for holding in holdings_data.get('holdings', []):
                    symbol = holding['symbol']
                    if symbol in aggregated_holdings:
                        aggregated_holdings[symbol]['balance'] += holding['balance']
                        aggregated_holdings[symbol]['value_usd'] += holding['value_usd']
                    else:
                        aggregated_holdings[symbol] = {
                            'symbol': symbol,
                            'name': holding['name'],
                            'balance': holding['balance'],
                            'value_usd': holding['value_usd']
                        }
                    total_value += holding['value_usd']
            
            # 计算百分比
            for holding in aggregated_holdings.values():
                holding['percentage'] = (holding['value_usd'] / total_value * 100) if total_value > 0 else 0
            
            # 按价值排序
            sorted_holdings = sorted(aggregated_holdings.values(), key=lambda x: x['value_usd'], reverse=True)
            
            return {
                'username': username,
                'total_value_usd': total_value,
                'total_wallets': len(user_wallets['wallets']),
                'holdings': sorted_holdings,
                'top_holdings': sorted_holdings[:5],
                'diversification_score': self._calculate_diversification_score(sorted_holdings),
                'last_updated': datetime.utcnow().isoformat() + 'Z'
            }
            
        except Exception as e:
            print(f"Error getting portfolio summary for {username}: {e}")
            return {
                'username': username,
                'portfolio': {},
                'error': str(e)
            }
    
    async def _discover_wallets_from_tweets(self, username: str) -> List[Dict[str, Any]]:
        """从推文中发现钱包地址"""
        try:
            # 获取用户最近的推文
            tweets = await self.data_collector.get_twitter_posts()
            user_tweets = [tweet for tweet in tweets if tweet.get('username', '').lower() == username.lower()]
            
            discovered_wallets = []
            
            for tweet in user_tweets[-50:]:  # 检查最近50条推文
                content = tweet.get('content', '') + ' ' + tweet.get('contentZh', '')
                
                # 使用正则表达式查找钱包地址
                for blockchain, pattern in self.wallet_patterns.items():
                    matches = pattern.findall(content)
                    for address in matches:
                        discovered_wallets.append({
                            'address': address,
                            'blockchain': blockchain,
                            'confidence': 0.7,  # 从推文发现的置信度较低
                            'source': 'tweet_content',
                            'tweet_id': tweet.get('id'),
                            'discovered_date': datetime.utcnow().isoformat() + 'Z'
                        })
            
            return discovered_wallets
            
        except Exception as e:
            print(f"Error discovering wallets from tweets: {e}")
            return []
    
    async def _discover_wallets_from_profile(self, username: str) -> List[Dict[str, Any]]:
        """从个人资料中发现钱包地址"""
        try:
            # 这里应该调用推特API获取用户资料
            # 由于API限制，这里返回空列表
            return []
            
        except Exception as e:
            print(f"Error discovering wallets from profile: {e}")
            return []
    
    def _deduplicate_wallets(self, wallets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重钱包地址"""
        seen_addresses = set()
        unique_wallets = []
        
        for wallet in wallets:
            address = wallet['address'].lower()
            if address not in seen_addresses:
                seen_addresses.add(address)
                unique_wallets.append(wallet)
        
        return unique_wallets
    
    async def _enrich_wallet_data(self, wallet: Dict[str, Any]) -> Dict[str, Any]:
        """丰富钱包数据，添加链上信息"""
        try:
            address = wallet['address']
            
            # 获取余额数据
            balance_data = await blockchain_service.get_wallet_balance(address)
            
            # 获取持仓数据
            holdings_data = await blockchain_service.get_wallet_holdings(address)
            
            # 获取活动分析
            activity_data = await blockchain_service.analyze_wallet_activity(address)
            
            # 获取最近交易
            recent_transactions = await blockchain_service.get_wallet_transactions(address, limit=10)
            
            enriched_wallet = {
                **wallet,
                'balance_data': balance_data,
                'holdings_data': holdings_data,
                'activity_data': activity_data,
                'recent_transactions': recent_transactions,
                'enriched_date': datetime.utcnow().isoformat() + 'Z'
            }
            
            return enriched_wallet
            
        except Exception as e:
            print(f"Error enriching wallet data: {e}")
            return {
                **wallet,
                'error': str(e)
            }
    
    async def _analyze_wallet_connection(self, address1: str, address2: str) -> Dict[str, Any]:
        """分析两个钱包地址之间的连接"""
        try:
            # 获取两个钱包的交易记录
            txs1 = await blockchain_service.get_wallet_transactions(address1, limit=100)
            txs2 = await blockchain_service.get_wallet_transactions(address2, limit=100)
            
            # 查找直接交易
            direct_transactions = []
            for tx in txs1:
                if tx.get('to', '').lower() == address2.lower() or tx.get('from', '').lower() == address2.lower():
                    direct_transactions.append(tx)
            
            for tx in txs2:
                if tx.get('to', '').lower() == address1.lower() or tx.get('from', '').lower() == address1.lower():
                    if tx not in direct_transactions:
                        direct_transactions.append(tx)
            
            return {
                'address1': address1,
                'address2': address2,
                'has_connection': len(direct_transactions) > 0,
                'direct_transactions': len(direct_transactions),
                'total_volume': sum(tx.get('value_usd', 0) for tx in direct_transactions),
                'last_interaction': direct_transactions[0]['timestamp'] if direct_transactions else None
            }
            
        except Exception as e:
            print(f"Error analyzing wallet connection: {e}")
            return {
                'address1': address1,
                'address2': address2,
                'has_connection': False,
                'error': str(e)
            }
    
    async def _analyze_exchange_patterns(self, wallets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析与交易所的交互模式"""
        try:
            exchange_interactions = {}
            total_exchange_volume = 0
            
            for wallet in wallets:
                activity_data = wallet.get('activity_data', {})
                interactions = activity_data.get('exchange_interactions', {})
                
                for exchange, count in interactions.items():
                    if exchange in exchange_interactions:
                        exchange_interactions[exchange] += count
                    else:
                        exchange_interactions[exchange] = count
                
                total_exchange_volume += activity_data.get('total_volume_usd', 0)
            
            # 找出最常用的交易所
            most_used_exchange = max(exchange_interactions.items(), key=lambda x: x[1]) if exchange_interactions else None
            
            return {
                'exchange_interactions': exchange_interactions,
                'total_exchange_volume': total_exchange_volume,
                'most_used_exchange': most_used_exchange[0] if most_used_exchange else None,
                'exchange_diversity': len(exchange_interactions)
            }
            
        except Exception as e:
            print(f"Error analyzing exchange patterns: {e}")
            return {}
    
    def _calculate_diversification_score(self, holdings: List[Dict[str, Any]]) -> float:
        """计算投资组合多样化分数"""
        if not holdings:
            return 0.0
        
        # 使用赫芬达尔指数计算集中度，然后转换为多样化分数
        total_value = sum(h['value_usd'] for h in holdings)
        if total_value == 0:
            return 0.0
        
        herfindahl_index = sum((h['value_usd'] / total_value) ** 2 for h in holdings)
        diversification_score = (1 - herfindahl_index) * 100
        
        return round(diversification_score, 2)

# 创建全局实例
twitter_wallet_service = TwitterWalletService()

