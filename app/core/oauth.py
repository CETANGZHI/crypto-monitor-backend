from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from app.core.config import settings

# OAuth2配置
config = Config()

oauth = OAuth(config)

# Google OAuth2配置
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Apple OAuth2配置
oauth.register(
    name='apple',
    client_id=settings.APPLE_CLIENT_ID,
    client_secret=settings.APPLE_CLIENT_SECRET,
    authorize_url='https://appleid.apple.com/auth/authorize',
    access_token_url='https://appleid.apple.com/auth/token',
    client_kwargs={
        'scope': 'name email',
        'response_mode': 'form_post'
    }
)

class OAuthService:
    """OAuth2服务类"""
    
    def __init__(self):
        self.oauth = oauth
    
    def get_google_client(self):
        """获取Google OAuth客户端"""
        return self.oauth.google
    
    def get_apple_client(self):
        """获取Apple OAuth客户端"""
        return self.oauth.apple
    
    async def get_google_user_info(self, token):
        """获取Google用户信息"""
        try:
            google = self.get_google_client()
            resp = await google.parse_id_token(token)
            return {
                'provider': 'google',
                'provider_id': resp.get('sub'),
                'email': resp.get('email'),
                'name': resp.get('name'),
                'picture': resp.get('picture'),
                'email_verified': resp.get('email_verified', False)
            }
        except Exception as e:
            print(f"获取Google用户信息失败: {e}")
            return None
    
    async def get_apple_user_info(self, token):
        """获取Apple用户信息"""
        try:
            apple = self.get_apple_client()
            resp = await apple.parse_id_token(token)
            return {
                'provider': 'apple',
                'provider_id': resp.get('sub'),
                'email': resp.get('email'),
                'name': resp.get('name'),
                'email_verified': resp.get('email_verified', False)
            }
        except Exception as e:
            print(f"获取Apple用户信息失败: {e}")
            return None

# 创建全局OAuth服务实例
oauth_service = OAuthService()

