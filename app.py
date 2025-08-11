from flask import Flask
from app.main import app as fastapi_app
import uvicorn
import threading
import time

# 创建Flask应用
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return {
        "message": "币圈监控平台API服务正在运行",
        "version": "1.0.0",
        "status": "healthy"
    }

@flask_app.route('/health')
def health():
    return {
        "status": "healthy",
        "service": "crypto-monitor-backend"
    }

# 在后台运行FastAPI
def run_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8001)

# 启动FastAPI服务
fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
fastapi_thread.start()

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8000, debug=False)

