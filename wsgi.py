from app.main import app

# Flask兼容性包装
class FlaskCompatApp:
    def __init__(self, fastapi_app):
        self.fastapi_app = fastapi_app
    
    def run(self, host="0.0.0.0", port=8000, debug=False):
        import uvicorn
        uvicorn.run(self.fastapi_app, host=host, port=port)

# 创建Flask兼容的app实例
application = FlaskCompatApp(app)

if __name__ == "__main__":
    application.run()
