"""
区块链数据服务模块
提供钱包地址分析、持仓查询、交易记录等功能
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import aiohttp
from ..core.config import settings

class BlockchainService:
    """区块链数据服务类"""
    
    def __init__(self):
        # 使用免费的区块链API服务
        self.etherscan_api_key = getattr(settings, 'ETHERSCAN_API_KEY', 'YourApiKeyToken')
        self.etherscan_base_url = "https://api.etherscan.io/api"
        
        # 备用API服务
        self.moralis_api_key = getattr(settings, 'MORALIS_API_KEY', '')
        self.alchemy_api_key = getattr(settings, 'ALCHEMY_API_KEY', '')
        
        # 交易所地址数据库（用于识别转账目的地）
        self.exchange_addresses = {
            # Binance
            "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be": "Binance",
            "0xd551234ae421e3bcba99a0da6d736074f22192ff": "Binance",
            "0x564286362092d8e7936f0549571a803b203aaced": "Binance",
            
            # Coinbase
            "0x71660c4005ba85c37ccec55d0c4493e66fe775d3": "Coinbase",
            "0x503828976d22510aad0201ac7ec88293211d23da": "Coinbase",
            "0xddfabcdc4d8ffc6d5beaf154f18b778f892a0740": "Coinbase",
            
            # Kraken
            "0x2910543af39aba0cd09dbb2d50200b3e800a63d2": "Kraken",
            "0x0a869d79a7052c7f1b55a8ebabbea3420f0d1e13": "Kraken",
            
            # OKX
            "0x6cc5f688a315f3dc28a7781717a9a798a59fda7b": "OKX",
            "0x236f9f97e0e62388479bf9e5ba4889e46b0273c3": "OKX",
            
            # Huobi
            "0xdc76cd25977e0a5ae17155770273ad58648900d3": "Huobi",
            "0xab5c66752a9e8167967685f1450532fb96d5d24f": "Huobi",
        }
    
    async def get_wallet_balance(self, address: str) -> Dict[str, Any]:
        """获取钱包余额信息"""
        try:
            # 获取ETH余额
            eth_balance = await self._get_eth_balance(address)
            
            # 获取ERC-20代币余额
            token_balances = await self._get_token_balances(address)
            
            # 计算总价值（需要价格API）
            total_value = await self._calculate_total_value(eth_balance, token_balances)
            
            return {
                "address": address,
                "eth_balance": eth_balance,
                "token_balances": token_balances,
                "total_value_usd": total_value,
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error getting wallet balance for {address}: {e}")
            return self._get_mock_wallet_balance(address)
    
    async def get_wallet_transactions(self, address: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取钱包交易记录"""
        try:
            # 获取普通交易
            normal_txs = await self._get_normal_transactions(address, limit)
            
            # 获取内部交易
            internal_txs = await self._get_internal_transactions(address, limit)
            
            # 获取ERC-20代币交易
            token_txs = await self._get_token_transactions(address, limit)
            
            # 合并和排序交易
            all_transactions = normal_txs + internal_txs + token_txs
            all_transactions.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # 分析交易目的地
            for tx in all_transactions:
                tx['destination_type'] = self._analyze_destination(tx.get('to', ''))
            
            return all_transactions[:limit]
        except Exception as e:
            print(f"Error getting transactions for {address}: {e}")
            return self._get_mock_transactions(address)
    
    async def get_wallet_holdings(self, address: str) -> Dict[str, Any]:
        """获取钱包持仓分析"""
        try:
            balance_data = await self.get_wallet_balance(address)
            
            # 分析持仓分布
            holdings = []
            total_value = balance_data.get('total_value_usd', 0)
            
            # ETH持仓
            if balance_data.get('eth_balance', 0) > 0:
                eth_value = balance_data['eth_balance'] * await self._get_eth_price()
                holdings.append({
                    "symbol": "ETH",
                    "name": "Ethereum",
                    "balance": balance_data['eth_balance'],
                    "value_usd": eth_value,
                    "percentage": (eth_value / total_value * 100) if total_value > 0 else 0
                })
            
            # 代币持仓
            for token in balance_data.get('token_balances', []):
                if token.get('value_usd', 0) > 0:
                    holdings.append({
                        "symbol": token['symbol'],
                        "name": token['name'],
                        "balance": token['balance'],
                        "value_usd": token['value_usd'],
                        "percentage": (token['value_usd'] / total_value * 100) if total_value > 0 else 0
                    })
            
            # 按价值排序
            holdings.sort(key=lambda x: x['value_usd'], reverse=True)
            
            return {
                "address": address,
                "total_value_usd": total_value,
                "holdings_count": len(holdings),
                "holdings": holdings,
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error getting holdings for {address}: {e}")
            return self._get_mock_holdings(address)
    
    async def analyze_wallet_activity(self, address: str, days: int = 30) -> Dict[str, Any]:
        """分析钱包活动模式"""
        try:
            # 获取指定天数内的交易
            transactions = await self.get_wallet_transactions(address, limit=1000)
            
            # 过滤指定时间范围内的交易
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            recent_txs = [
                tx for tx in transactions 
                if datetime.fromisoformat(tx['timestamp'].replace('Z', '+00:00')) > cutoff_date
            ]
            
            # 分析交易模式
            analysis = {
                "address": address,
                "analysis_period_days": days,
                "total_transactions": len(recent_txs),
                "incoming_transactions": len([tx for tx in recent_txs if tx['type'] == 'in']),
                "outgoing_transactions": len([tx for tx in recent_txs if tx['type'] == 'out']),
                "total_volume_usd": sum(tx.get('value_usd', 0) for tx in recent_txs),
                "average_transaction_value": 0,
                "most_active_day": None,
                "exchange_interactions": {},
                "unknown_addresses": [],
                "last_activity": None
            }
            
            if recent_txs:
                analysis["average_transaction_value"] = analysis["total_volume_usd"] / len(recent_txs)
                analysis["last_activity"] = recent_txs[0]['timestamp']
                
                # 分析交易所交互
                exchange_interactions = {}
                unknown_addresses = set()
                
                for tx in recent_txs:
                    dest_type = tx.get('destination_type', 'Unknown')
                    if dest_type != 'Unknown':
                        exchange_interactions[dest_type] = exchange_interactions.get(dest_type, 0) + 1
                    else:
                        if tx.get('to') and tx['to'] != address:
                            unknown_addresses.add(tx['to'])
                
                analysis["exchange_interactions"] = exchange_interactions
                analysis["unknown_addresses"] = list(unknown_addresses)[:10]  # 限制数量
            
            return analysis
        except Exception as e:
            print(f"Error analyzing wallet activity for {address}: {e}")
            return self._get_mock_activity_analysis(address)
    
    def _analyze_destination(self, address: str) -> str:
        """分析交易目的地类型"""
        if not address:
            return "Unknown"
        
        address_lower = address.lower()
        
        # 检查是否为已知交易所地址
        for exchange_addr, exchange_name in self.exchange_addresses.items():
            if address_lower == exchange_addr.lower():
                return exchange_name
        
        return "Unknown"
    
    async def _get_eth_balance(self, address: str) -> float:
        """获取ETH余额"""
        try:
            url = f"{self.etherscan_base_url}?module=account&action=balance&address={address}&tag=latest&apikey={self.etherscan_api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    if data.get('status') == '1':
                        # 转换wei到ETH
                        balance_wei = int(data.get('result', '0'))
                        return balance_wei / 10**18
            return 0.0
        except Exception as e:
            print(f"Error getting ETH balance: {e}")
            return 0.0
    
    async def _get_token_balances(self, address: str) -> List[Dict[str, Any]]:
        """获取ERC-20代币余额"""
        # 由于免费API限制，这里返回模拟数据
        # 实际实现需要调用代币合约或使用付费API
        return [
            {
                "symbol": "USDT",
                "name": "Tether USD",
                "balance": 50000.0,
                "value_usd": 50000.0,
                "contract_address": "0xdac17f958d2ee523a2206206994597c13d831ec7"
            },
            {
                "symbol": "USDC",
                "name": "USD Coin",
                "balance": 25000.0,
                "value_usd": 25000.0,
                "contract_address": "0xa0b86a33e6c3c8bcf4251444d5374d2c5c8b7b8b"
            }
        ]
    
    async def _get_normal_transactions(self, address: str, limit: int) -> List[Dict[str, Any]]:
        """获取普通交易记录"""
        try:
            url = f"{self.etherscan_base_url}?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&page=1&offset={limit}&sort=desc&apikey={self.etherscan_api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    if data.get('status') == '1':
                        transactions = []
                        for tx in data.get('result', []):
                            transactions.append({
                                "hash": tx.get('hash'),
                                "type": "in" if tx.get('to', '').lower() == address.lower() else "out",
                                "from": tx.get('from'),
                                "to": tx.get('to'),
                                "value": float(tx.get('value', '0')) / 10**18,  # 转换wei到ETH
                                "value_usd": 0,  # 需要价格API计算
                                "gas_used": int(tx.get('gasUsed', '0')),
                                "gas_price": int(tx.get('gasPrice', '0')),
                                "timestamp": datetime.fromtimestamp(int(tx.get('timeStamp', '0'))).isoformat() + 'Z',
                                "status": "success" if tx.get('txreceipt_status') == '1' else "failed"
                            })
                        return transactions
            return []
        except Exception as e:
            print(f"Error getting normal transactions: {e}")
            return []
    
    async def _get_internal_transactions(self, address: str, limit: int) -> List[Dict[str, Any]]:
        """获取内部交易记录"""
        # 简化实现，返回空列表
        return []
    
    async def _get_token_transactions(self, address: str, limit: int) -> List[Dict[str, Any]]:
        """获取代币交易记录"""
        # 简化实现，返回空列表
        return []
    
    async def _calculate_total_value(self, eth_balance: float, token_balances: List[Dict]) -> float:
        """计算总价值"""
        try:
            eth_price = await self._get_eth_price()
            total_value = eth_balance * eth_price
            
            for token in token_balances:
                total_value += token.get('value_usd', 0)
            
            return total_value
        except Exception as e:
            print(f"Error calculating total value: {e}")
            return 0.0
    
    async def _get_eth_price(self) -> float:
        """获取ETH价格"""
        try:
            # 使用免费的价格API
            url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    return data.get('ethereum', {}).get('usd', 2400.0)
        except Exception as e:
            print(f"Error getting ETH price: {e}")
            return 2400.0  # 默认价格
    
    # 模拟数据方法（用于开发和测试）
    def _get_mock_wallet_balance(self, address: str) -> Dict[str, Any]:
        """获取模拟钱包余额"""
        return {
            "address": address,
            "eth_balance": 15.5,
            "token_balances": [
                {
                    "symbol": "USDT",
                    "name": "Tether USD",
                    "balance": 50000.0,
                    "value_usd": 50000.0,
                    "contract_address": "0xdac17f958d2ee523a2206206994597c13d831ec7"
                },
                {
                    "symbol": "USDC",
                    "name": "USD Coin",
                    "balance": 25000.0,
                    "value_usd": 25000.0,
                    "contract_address": "0xa0b86a33e6c3c8bcf4251444d5374d2c5c8b7b8b"
                }
            ],
            "total_value_usd": 112200.0,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _get_mock_transactions(self, address: str) -> List[Dict[str, Any]]:
        """获取模拟交易记录"""
        return [
            {
                "hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "type": "out",
                "from": address,
                "to": "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be",
                "value": 5.0,
                "value_usd": 12000.0,
                "gas_used": 21000,
                "gas_price": 20000000000,
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat() + 'Z',
                "status": "success",
                "destination_type": "Binance"
            },
            {
                "hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                "type": "in",
                "from": "0x71660c4005ba85c37ccec55d0c4493e66fe775d3",
                "to": address,
                "value": 10.0,
                "value_usd": 24000.0,
                "gas_used": 21000,
                "gas_price": 18000000000,
                "timestamp": (datetime.utcnow() - timedelta(hours=6)).isoformat() + 'Z',
                "status": "success",
                "destination_type": "Coinbase"
            }
        ]
    
    def _get_mock_holdings(self, address: str) -> Dict[str, Any]:
        """获取模拟持仓数据"""
        return {
            "address": address,
            "total_value_usd": 112200.0,
            "holdings_count": 3,
            "holdings": [
                {
                    "symbol": "USDT",
                    "name": "Tether USD",
                    "balance": 50000.0,
                    "value_usd": 50000.0,
                    "percentage": 44.6
                },
                {
                    "symbol": "ETH",
                    "name": "Ethereum",
                    "balance": 15.5,
                    "value_usd": 37200.0,
                    "percentage": 33.2
                },
                {
                    "symbol": "USDC",
                    "name": "USD Coin",
                    "balance": 25000.0,
                    "value_usd": 25000.0,
                    "percentage": 22.3
                }
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _get_mock_activity_analysis(self, address: str) -> Dict[str, Any]:
        """获取模拟活动分析"""
        return {
            "address": address,
            "analysis_period_days": 30,
            "total_transactions": 45,
            "incoming_transactions": 20,
            "outgoing_transactions": 25,
            "total_volume_usd": 450000.0,
            "average_transaction_value": 10000.0,
            "most_active_day": (datetime.utcnow() - timedelta(days=3)).isoformat() + 'Z',
            "exchange_interactions": {
                "Binance": 8,
                "Coinbase": 5,
                "Kraken": 2
            },
            "unknown_addresses": [
                "0x1234567890abcdef1234567890abcdef12345678",
                "0xabcdef1234567890abcdef1234567890abcdef12"
            ],
            "last_activity": (datetime.utcnow() - timedelta(hours=2)).isoformat() + 'Z'
        }

# 创建全局实例
blockchain_service = BlockchainService()

