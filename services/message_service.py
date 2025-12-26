"""
Message service for generating professional messages
"""
from datetime import datetime
from utils.text_utils import escape_markdown_v2, format_separator, get_user_display_name
from services.user_service import UserService


class MessageService:
    """Service for generating professional bot messages"""
    
    @staticmethod
    def generate_welcome_message(user, is_new_user: bool = False) -> str:
        """
        Generate professional welcome message.
        
        Args:
            user: Telegram User object
            is_new_user: Whether this is user's first interaction
            
        Returns:
            Formatted welcome message in MarkdownV2
        """
        user_display_name = get_user_display_name(user)
        
        # Get current time for greeting
        current_hour = datetime.utcnow().hour
        if 5 <= current_hour < 12:
            time_greeting = "早上好"
        elif 12 <= current_hour < 18:
            time_greeting = "下午好"
        elif 18 <= current_hour < 22:
            time_greeting = "晚上好"
        else:
            time_greeting = "您好"
        
        # New user vs returning user greeting
        if is_new_user:
            welcome_line = f"👋 *{time_greeting}，{user_display_name}！欢迎加入伍拾支付生态系统*"
            status_note = "*首次登录成功，您的专属账户已激活*"
        else:
            welcome_line = f"👋 *{time_greeting}，{user_display_name}！欢迎回来*"
            user_data = UserService.get_user(user.id)
            if user_data:
                status_note = f"*账户状态：正常 \\| 消息数：{user_data.get('message_count', 0)}*"
            else:
                status_note = "*账户状态：正常*"
        
        # User info section
        user_info_parts = []
        if user.username:
            user_info_parts.append(f"👤 *Telegram*: `@{escape_markdown_v2(user.username)}`")
        if user.id:
            user_info_parts.append(f"🆔 *UID*: `{user.id}`")
        if getattr(user, "is_premium", False):
            user_info_parts.append("⭐ *Premium 会员*")
        
        user_info_text = ""
        if user_info_parts:
            user_info_text = "\n".join(user_info_parts) + "\n\n"
        
        # System status with timestamp
        current_time = datetime.utcnow().strftime("%Y\\-%m\\-%d %H:%M UTC")
        
        # Professional welcome message
        welcome_text = (
            f"{welcome_line}\n"
            f"{status_note}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "*系统状态实时监控*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🟢 *服务状态*: 在线 \\(100\\%\\)\n"
            "🔒 *安全通道*: TLS 1\\.3 已建立\n"
            "⚡ *响应时间*: < 50ms\n"
            "🛡️  *风控系统*: 实时监控中\n"
            f"📅 *当前时间*: `{current_time}`\n"
            f"{user_info_text}"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"尊敬的 {user_display_name}，\n\n"
            "欢迎访问 *伍拾支付* 企业级自动化结算中心。\n\n"
            "我们为您提供：\n"
            "• *7×24小时* 不间断服务\n"
            "• *企业级* 代收代付解决方案\n"
            "• *银行级* 资金安全保障\n"
            "• *毫秒级* 交易处理速度\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "*今日汇率概览*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🇺🇸 `USDT/CNY`: *7\\.42* \\(实时锁定\\)\n"
            "⚡ *平均到账时效*: *3\\.2秒*\n"
            "💱 *24H 交易量*: *$12\\.8M*\n\n"
            "👇 *请选择您的操作终端：*"
        )
        
        return welcome_text
    
    @staticmethod
    def generate_rates_message() -> str:
        """
        Generate professional rates information message.
        
        Returns:
            Formatted rates message in MarkdownV2
        """
        rates_text = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "*费率标准与服务条款*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "*支付通道费率*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💳 *支付宝通道*\n"
            "   标准费率: *0\\.6\\%*\n"
            "   到账时间: *即时到账*\n"
            "   单笔限额: ¥1\\-500,000\n\n"
            "🍀 *微信支付通道*\n"
            "   标准费率: *0\\.6\\%*\n"
            "   到账时间: *即时到账*\n"
            "   单笔限额: ¥1\\-500,000\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "*VIP 费率优惠*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⭐ *VIP1*: 月交易量 > ¥100万 → *0\\.55\\%*\n"
            "⭐ *VIP2*: 月交易量 > ¥500万 → *0\\.50\\%*\n"
            "⭐ *VIP3*: 月交易量 > ¥1000万 → *0\\.45\\%*\n\n"
            "💼 企业客户可联系商务合作获取专属费率\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "*服务条款*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "• 所有费率均为实时报价\n"
            "• 结算周期: T\\+0 \\(当日到账\\)\n"
            "• 支持退款与售后服务\n"
            "• 7×24小时技术支持\n\n"
            "📞 详情请联系专属客服"
        )
        
        return rates_text

