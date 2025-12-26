"""
Message service for generating professional messages
"""
import asyncio
import os
from datetime import datetime
from pathlib import Path
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
    
    @staticmethod
    def get_logo_path() -> str:
        """
        Get logo file path.
        Prefers PNG files with transparency (alpha channel).
        
        Note: For transparent background to work properly:
        - PNG file must have an alpha channel (transparency layer)
        - File should be saved as PNG-24 or PNG-32 (not PNG-8)
        - Use tools like Photoshop, GIMP, or online converters to ensure transparency
        """
        # Try multiple possible locations
        # __file__ is in services/message_service.py, so parent.parent is wushizhifu-bot directory
        possible_paths = [
            Path(__file__).parent.parent / "logo_300.png",  # wushizhifu-bot/logo_300.png (preferred)
            Path(__file__).parent.parent / "logo.png",      # wushizhifu-bot/logo.png
            Path(__file__).parent.parent.parent / "logo_300.png",  # parent project root
            Path(__file__).parent.parent.parent / "logo.png",      # parent project root
        ]
        
        for path in possible_paths:
            try:
                if path.exists():
                    # Verify it's a PNG file
                    if path.suffix.lower() in ['.png']:
                        return str(path.absolute())
            except Exception:
                continue
        
        # Return None if not found
        return None
    
    @staticmethod
    def generate_loading_animation() -> str:
        """Generate loading animation message"""
        return (
            "⏳ *正在初始化系统\\.\\.\\.*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "█▒▒▒▒▒▒▒▒▒▒ *10\\%*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
    
    @staticmethod
    def generate_welcome_card(user, is_new_user: bool = False) -> str:
        """Generate personalized welcome card (Step 2) - Simplified without borders"""
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
        
        user_info_parts = []
        if user.username:
            user_info_parts.append(f"👤 *Telegram*: `@{escape_markdown_v2(user.username)}`")
        if user.id:
            user_info_parts.append(f"🆔 *UID*: `{escape_markdown_v2(str(user.id))}`")
        if getattr(user, "is_premium", False):
            user_info_parts.append("⭐ *Premium 会员*")
        
        user_info_text = "\n".join(user_info_parts) if user_info_parts else ""
        
        # Get user data for status
        user_data = UserService.get_user(user.id)
        message_count = user_data.get('message_count', 0) if user_data else 0
        
        if is_new_user:
            welcome_title = f"🎉 *欢迎加入伍拾支付生态系统\\!*"
            status_line = "*首次登录成功，您的专属账户已激活*"
        else:
            welcome_title = f"✨ *{time_greeting}，{escape_markdown_v2(user_display_name)} \\!*"
            status_line = f"*账户状态: 正常 \\| 消息数: {message_count}*"
        
        card_text = f"{welcome_title}\n{status_line}"
        
        if user_info_text:
            card_text += f"\n{user_info_text}"
        
        return card_text
    
    @staticmethod
    def generate_system_status_panel() -> str:
        """Generate system status monitoring panel (Step 3) - Simplified without borders"""
        current_time = datetime.utcnow().strftime("%Y\\-%m\\-%d %H:%M UTC")
        
        panel_text = (
            "📊 *系统状态实时监控*\n\n"
            "🟢 *服务状态*: 在线 \\(100\\%\\) \\|\n"
            "🔒 *安全通道*: TLS 1\\.3 已建立 \\|\n"
            "⚡ *响应时间*: < 50ms \\|\n"
            "🛡️  *风控系统*: 实时监控中 \\|\n"
            f"📅 *当前时间*: `{current_time}`"
        )
        
        return panel_text
    
    @staticmethod
    async def generate_service_highlights_typing(message_obj, user_display_name: str = None):
        """
        Generate service highlights with typing effect (Step 4)
        Types out all text character by character within 3 seconds
        
        Args:
            message_obj: Message object for sending messages
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # All text to type out (excluding emojis from character count)
        title_part = "💎 伍拾支付企业级自动化结算中心"
        intro_part = "✨ 我们为您提供："
        services = [
            "🕐 7×24小时 不间断服务",
            "🏢 企业级 代收代付解决方案",
            "🏦 银行级 资金安全保障",
            "⚡ 毫秒级 交易处理速度"
        ]
        
        # Calculate total characters (approximate, excluding emojis)
        total_chars = len(title_part) + 2 + len(intro_part) + 2  # +2 for \n\n
        for service in services:
            total_chars += len(service) + 1  # +1 for \n
        total_chars -= 5  # Subtract emoji count (they render as single chars but don't need typing delay)
        
        # Target: 3 seconds total, so delay per character
        # Use slightly faster to account for processing time
        char_delay = 2.5 / total_chars if total_chars > 0 else 0.03  # Max 2.5 seconds, leave buffer
        
        try:
            # Send initial message with properly escaped cursor
            cursor_text = escape_markdown_v2("_")
            current_msg = await message_obj.answer(
                text=cursor_text,
                parse_mode="MarkdownV2"
            )
            
            typed_text = ""
            
            # Type out title character by character
            for char in title_part:
                typed_text += char
                escaped_text = escape_markdown_v2(f"{typed_text}_")
                try:
                    await current_msg.edit_text(
                        text=escaped_text,
                        parse_mode="MarkdownV2"
                    )
                except Exception as e:
                    logger.warning(f"Error editing during title typing: {e}")
                await asyncio.sleep(char_delay)
            
            # Add newlines
            typed_text += "\n\n"
            escaped_text = escape_markdown_v2(f"{typed_text}_")
            try:
                await current_msg.edit_text(
                    text=escaped_text,
                    parse_mode="MarkdownV2"
                )
            except:
                pass
            await asyncio.sleep(char_delay * 2)
            
            # Type out intro line
            for char in intro_part:
                typed_text += char
                escaped_text = escape_markdown_v2(f"{typed_text}_")
                try:
                    await current_msg.edit_text(
                        text=escaped_text,
                        parse_mode="MarkdownV2"
                    )
                except:
                    pass
                await asyncio.sleep(char_delay)
            
            # Add newlines
            typed_text += "\n\n"
            escaped_text = escape_markdown_v2(f"{typed_text}_")
            try:
                await current_msg.edit_text(
                    text=escaped_text,
                    parse_mode="MarkdownV2"
                )
            except:
                pass
            await asyncio.sleep(char_delay * 2)
            
            # Type out each service line
            for service_line in services:
                for char in service_line:
                    typed_text += char
                    escaped_text = escape_markdown_v2(f"{typed_text}_")
                    try:
                        await current_msg.edit_text(
                            text=escaped_text,
                            parse_mode="MarkdownV2"
                        )
                    except:
                        pass
                    await asyncio.sleep(char_delay)
                # Add newline after each service
                typed_text += "\n"
                escaped_text = escape_markdown_v2(f"{typed_text}_")
                try:
                    await current_msg.edit_text(
                        text=escaped_text,
                        parse_mode="MarkdownV2"
                    )
                except:
                    pass
                await asyncio.sleep(char_delay)
            
            # Remove cursor and format final message with MarkdownV2
            final_text = (
                f"*{escape_markdown_v2('💎 伍拾支付企业级自动化结算中心')}*\n\n"
                f"*{escape_markdown_v2('✨ 我们为您提供：')}*\n\n"
                f"*{escape_markdown_v2('🕐 7×24小时')}* {escape_markdown_v2('不间断服务')}\n"
                f"*{escape_markdown_v2('🏢 企业级')}* {escape_markdown_v2('代收代付解决方案')}\n"
                f"*{escape_markdown_v2('🏦 银行级')}* {escape_markdown_v2('资金安全保障')}\n"
                f"*{escape_markdown_v2('⚡ 毫秒级')}* {escape_markdown_v2('交易处理速度')}"
            )
            
            try:
                await current_msg.edit_text(
                    text=final_text,
                    parse_mode="MarkdownV2"
                )
            except Exception as e:
                logger.warning(f"Error editing final formatted message: {e}")
                # If formatting fails, send new formatted message
                try:
                    await current_msg.delete()
                except:
                    pass
                await message_obj.answer(
                    text=final_text,
                    parse_mode="MarkdownV2"
                )
                
        except Exception as e:
            logger.error(f"Error in generate_service_highlights_typing: {e}", exc_info=True)
            # Fallback: send simple version without typing effect
            final_text = (
                f"*{escape_markdown_v2('💎 伍拾支付企业级自动化结算中心')}*\n\n"
                f"*{escape_markdown_v2('✨ 我们为您提供：')}*\n\n"
                f"*{escape_markdown_v2('🕐 7×24小时')}* {escape_markdown_v2('不间断服务')}\n"
                f"*{escape_markdown_v2('🏢 企业级')}* {escape_markdown_v2('代收代付解决方案')}\n"
                f"*{escape_markdown_v2('🏦 银行级')}* {escape_markdown_v2('资金安全保障')}\n"
                f"*{escape_markdown_v2('⚡ 毫秒级')}* {escape_markdown_v2('交易处理速度')}"
            )
            await message_obj.answer(
                text=final_text,
                parse_mode="MarkdownV2"
            )
    
    @staticmethod
    def generate_exchange_rate_card() -> str:
        """Generate exchange rate card (Step 5) - Simplified without borders"""
        rate_card = (
            "📈 *今日汇率概览*\n\n"
            "🇺🇸 *USDT/CNY*: *7\\.42* \\(实时锁定\\) \\|\n"
            "⚡ *平均到账*: *3\\.2秒* \\|\n"
            "💱 *24H交易量*: *$12\\.8M*"
        )
        
        return rate_card
    
    @staticmethod
    def generate_action_prompt() -> str:
        """Generate action prompt (Step 7)"""
        return "👇 *请选择您的操作终端：*"
    
    @staticmethod
    def generate_logo_caption() -> str:
        """
        Generate caption for logo image.
        Note: When PNG has transparent background (alpha channel), 
        it will blend perfectly with Telegram's chat background,
        creating an emoji-like effect.
        Simplified without borders for cleaner look.
        """
        return (
            "💎 *伍拾支付 WUSHI PAY* 💎\n"
            "*Enterprise Payment Gateway*"
        )

