import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import redis
import json
from datetime import datetime, timedelta

# Redis连接（用于存储验证码）
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        # 这里使用测试配置，实际部署时需要配置真实的SMTP服务器
        self.smtp_server = "smtp.gmail.com"  # 示例：Gmail SMTP
        self.smtp_port = 587
        self.smtp_username = "your-email@gmail.com"  # 需要配置
        self.smtp_password = "your-app-password"     # 需要配置
        self.from_email = "your-email@gmail.com"     # 需要配置
    
    def generate_verification_code(self) -> str:
        """生成6位数字验证码"""
        return ''.join(random.choices(string.digits, k=6))
    
    def store_verification_code(self, email: str, code: str, expires_in: int = 300) -> bool:
        """
        存储验证码到Redis
        Args:
            email: 邮箱地址
            code: 验证码
            expires_in: 过期时间（秒），默认5分钟
        """
        try:
            key = f"verification_code:{email}"
            data = {
                "code": code,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
            }
            redis_client.setex(key, expires_in, json.dumps(data))
            return True
        except Exception as e:
            print(f"存储验证码失败: {e}")
            return False
    
    def verify_code(self, email: str, code: str) -> bool:
        """
        验证验证码
        Args:
            email: 邮箱地址
            code: 用户输入的验证码
        """
        try:
            key = f"verification_code:{email}"
            stored_data = redis_client.get(key)
            
            if not stored_data:
                return False
            
            data = json.loads(stored_data)
            stored_code = data.get("code")
            expires_at = datetime.fromisoformat(data.get("expires_at"))
            
            # 检查验证码是否正确且未过期
            if stored_code == code and datetime.utcnow() <= expires_at:
                # 验证成功后删除验证码
                redis_client.delete(key)
                return True
            
            return False
        except Exception as e:
            print(f"验证验证码失败: {e}")
            return False
    
    def send_verification_email(self, email: str, code: str) -> bool:
        """
        发送验证码邮件
        Args:
            email: 收件人邮箱
            code: 验证码
        """
        try:
            # 创建邮件内容
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = email
            msg['Subject'] = "币圈监控平台 - 邮箱验证码"
            
            # 邮件正文
            body = f"""
            <html>
            <body>
                <h2>币圈监控平台</h2>
                <p>您好！</p>
                <p>您正在注册币圈监控平台账号，您的验证码是：</p>
                <h1 style="color: #007bff; font-size: 32px; letter-spacing: 5px;">{code}</h1>
                <p>验证码有效期为5分钟，请及时使用。</p>
                <p>如果这不是您的操作，请忽略此邮件。</p>
                <br>
                <p>币圈监控平台团队</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # 在测试环境中，我们模拟发送成功
            # 实际部署时需要配置真实的SMTP服务器
            print(f"模拟发送验证码邮件到 {email}，验证码: {code}")
            return True
            
            # 实际发送邮件的代码（需要配置SMTP服务器）
            # server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            # server.starttls()
            # server.login(self.smtp_username, self.smtp_password)
            # text = msg.as_string()
            # server.sendmail(self.from_email, email, text)
            # server.quit()
            # return True
            
        except Exception as e:
            print(f"发送邮件失败: {e}")
            return False
    
    def send_verification_code(self, email: str) -> bool:
        """
        发送验证码（生成验证码、存储、发送邮件）
        Args:
            email: 邮箱地址
        """
        # 生成验证码
        code = self.generate_verification_code()
        
        # 存储验证码
        if not self.store_verification_code(email, code):
            return False
        
        # 发送邮件
        return self.send_verification_email(email, code)

# 创建全局邮件服务实例
email_service = EmailService()

