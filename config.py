"""
Configuration loader for WuShiPay Telegram Bot
Loads environment variables from .env file
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for bot settings"""
    
    # Bot Token from environment variable
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # Initial admin user IDs (will be created on database initialization)
    INITIAL_ADMINS: list[int] = [
        7974525763,
        5433982810
    ]
    
    # MiniApp URL
    MINIAPP_URL: str = "https://50zf.usdt2026.cc"
    
    # Support Telegram username
    SUPPORT_USERNAME: str = "wushizhifu_jianglai"
    SUPPORT_URL: str = f"https://t.me/{SUPPORT_USERNAME}"
    
    @classmethod
    def get_miniapp_url(cls, view: str = "dashboard", provider: str = None) -> str:
        """Generate MiniApp URL with parameters"""
        url = f"{cls.MINIAPP_URL}?view={view}"
        if provider:
            url += f"&provider={provider}"
        return url
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is not set in environment variables or .env file")
        return True

