from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """应用配置类"""
    
    # 项目基本信息
    PROJECT_NAME: str = "币圈监控平台"
    API_V1_STR: str = "/api/v1"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "crypto_monitor"
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Elasticsearch配置
    ELASTICSEARCH_HOST: str = "localhost"
    ELASTICSEARCH_PORT: int = 9200
    ELASTICSEARCH_INDEX_PREFIX: str = "crypto_monitor"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Twitter API配置
    TWITTER_BEARER_TOKEN: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = None
    
    # 区块链API配置
    ETHERSCAN_API_KEY: Optional[str] = None
    BSCSCAN_API_KEY: Optional[str] = None
    POLYGONSCAN_API_KEY: Optional[str] = None
    INFURA_PROJECT_ID: Optional[str] = None
    MORALIS_API_KEY: Optional[str] = None
    ALCHEMY_API_KEY: Optional[str] = None
    
    # 邮件配置
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # 短信配置
    SMS_API_KEY: Optional[str] = None
    SMS_API_SECRET: Optional[str] = None
    
    # 支付配置
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # OAuth2 配置
    GOOGLE_CLIENT_ID: str = "your-google-client-id"
    GOOGLE_CLIENT_SECRET: str = "your-google-client-secret"
    APPLE_CLIENT_ID: str = "your-apple-client-id"
    APPLE_CLIENT_SECRET: str = "your-apple-client-secret"
    
    # 前端URL（用于OAuth回调）
    FRONTEND_URL: str = "http://localhost:3000"
    
    # 试用期配置
    TRIAL_PERIOD_DAYS: int = 3
    TRIAL_MAX_FOLLOWS: int = 5
    
    # 监控配置
    TWITTER_MONITOR_INTERVAL: int = 60  # 秒
    WALLET_MONITOR_INTERVAL: int = 30   # 秒
    BLACKROCK_MONITOR_INTERVAL: int = 3600  # 秒（1小时）
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    # 开发模式
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局设置实例
settings = Settings()

