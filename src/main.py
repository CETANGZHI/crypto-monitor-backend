import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify
from flask_cors import CORS

# 创建Flask应用实例
app = Flask(__name__)

# 配置CORS
CORS(app, origins="*")

@app.route("/")
def root():
    """根路径健康检查"""
    return jsonify({
        "message": "币圈监控平台API服务正在运行",
        "version": "1.0.0",
        "status": "healthy"
    })

@app.route("/health")
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "service": "crypto-monitor-backend"
    })

@app.route("/api/v1/twitter/latest")
def get_latest_tweets():
    """获取最新推文"""
    # 模拟数据
    return jsonify({
        "status": "success",
        "data": [
            {
                "id": 1,
                "username": "elonmusk",
                "display_name": "Elon Musk",
                "content": "To the moon! 🚀 #Bitcoin",
                "created_at": "2024-01-11T10:30:00Z",
                "likes": 15420,
                "retweets": 3240,
                "replies": 890
            }
        ]
    })

@app.route("/api/v1/wallet/twitter/<username>")
def get_twitter_user_wallet(username):
    """获取推特用户钱包信息"""
    # 模拟数据
    return jsonify({
        "status": "success",
        "data": {
            "username": username,
            "wallets": [
                {
                    "address": "0x742d35Cc6634C0532925a3b8D0C9964E5Bfe4",
                    "blockchain": "ethereum",
                    "balance_eth": "1250.45",
                    "balance_usd": "2500900.00"
                }
            ]
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)

