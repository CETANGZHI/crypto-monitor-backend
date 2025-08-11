from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({
        "message": "币圈监控平台API服务正在运行",
        "version": "1.0.0",
        "status": "healthy"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "crypto-monitor-backend"
    })

# 模拟推特数据API
@app.route('/api/v1/twitter/influencers')
def get_twitter_influencers():
    mock_data = [
        {
            "id": "elonmusk",
            "username": "elonmusk",
            "display_name": "Elon Musk",
            "avatar_url": "https://pbs.twimg.com/profile_images/1683325380441128960/yRsRRjGO_400x400.jpg",
            "verified": True,
            "followers_count": 150000000,
            "following_count": 300,
            "bio": "Tesla, SpaceX, Neuralink, The Boring Company",
            "location": "Austin, Texas",
            "website": "https://tesla.com",
            "created_at": "2009-06-02T20:12:29.000Z",
            "latest_tweets": [
                {
                    "id": "1234567890",
                    "text": "Dogecoin to the moon! 🚀",
                    "created_at": "2024-01-15T10:30:00.000Z",
                    "retweet_count": 50000,
                    "like_count": 200000,
                    "reply_count": 10000
                }
            ]
        },
        {
            "id": "justinsuntron",
            "username": "justinsuntron",
            "display_name": "Justin Sun",
            "avatar_url": "https://pbs.twimg.com/profile_images/1234567890/avatar.jpg",
            "verified": True,
            "followers_count": 3000000,
            "following_count": 1000,
            "bio": "Founder of TRON",
            "location": "Singapore",
            "website": "https://tron.network",
            "created_at": "2017-03-15T08:20:00.000Z",
            "latest_tweets": [
                {
                    "id": "1234567891",
                    "text": "TRON ecosystem is growing rapidly! #TRX",
                    "created_at": "2024-01-15T09:15:00.000Z",
                    "retweet_count": 5000,
                    "like_count": 15000,
                    "reply_count": 2000
                }
            ]
        }
    ]
    return jsonify(mock_data)

# 钱包监控API
@app.route('/api/v1/wallet/twitter/<username>')
def get_twitter_user_wallet(username):
    wallet_data = {
        "elonmusk": {
            "user_info": {
                "username": "elonmusk",
                "display_name": "Elon Musk",
                "avatar_url": "https://pbs.twimg.com/profile_images/1683325380441128960/yRsRRjGO_400x400.jpg",
                "verified": True,
                "followers_count": 150000000
            },
            "wallets": [
                {
                    "address": "0x742d35Cc6634C0532925a3b8D4C2C4e07C3C4C4C",
                    "blockchain": "ethereum",
                    "confidence": 0.9,
                    "source": "twitter_bio",
                    "balance_usd": 50000000,
                    "tokens": [
                        {"symbol": "ETH", "balance": "15000", "value_usd": 45000000},
                        {"symbol": "DOGE", "balance": "10000000", "value_usd": 5000000}
                    ]
                }
            ]
        },
        "justinsuntron": {
            "user_info": {
                "username": "justinsuntron", 
                "display_name": "Justin Sun",
                "avatar_url": "https://pbs.twimg.com/profile_images/1234567890/avatar.jpg",
                "verified": True,
                "followers_count": 3000000
            },
            "wallets": [
                {
                    "address": "TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7",
                    "blockchain": "tron",
                    "confidence": 0.98,
                    "source": "official_announcement",
                    "balance_usd": 100000000,
                    "tokens": [
                        {"symbol": "TRX", "balance": "1000000000", "value_usd": 80000000},
                        {"symbol": "USDT", "balance": "20000000", "value_usd": 20000000}
                    ]
                }
            ]
        }
    }
    
    if username in wallet_data:
        return jsonify(wallet_data[username])
    else:
        return jsonify({"error": "User not found"}), 404

# 贝莱德持仓API
@app.route('/api/v1/blackrock/holdings')
def get_blackrock_holdings():
    return jsonify({
        "btc": {
            "current_holdings": 350000,
            "value_usd": 15750000000,
            "change_1d": 2500,
            "change_7d": 12000,
            "change_30d": 45000,
            "percentage_change_1d": 0.72,
            "percentage_change_7d": 3.55,
            "percentage_change_30d": 14.75
        },
        "eth": {
            "current_holdings": 2800000,
            "value_usd": 8400000000,
            "change_1d": 15000,
            "change_7d": 85000,
            "change_30d": 280000,
            "percentage_change_1d": 0.54,
            "percentage_change_7d": 3.13,
            "percentage_change_30d": 11.11
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)

