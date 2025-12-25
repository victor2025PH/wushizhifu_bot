"""
Main keyboard layouts for WuShiPay Telegram Bot
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import Config


def get_main_keyboard() -> InlineKeyboardMarkup:
    """
    Returns the main inline keyboard for the bot.
    
    Layout:
    - Row 1: Launch Mini App button
    - Row 2: Alipay and WeChat payment channels (跳轉到 MiniApp)
    - Row 3: Transaction records and Calculator (跳轉到 MiniApp)
    - Row 4: Wallet and Settings (跳轉到 MiniApp)
    - Row 5: Statistics (Bot 內顯示)
    - Row 6: Support and AI Assistant
    - Row 7: Admin Panel (僅管理員可見)
    
    Args:
        user_id: User ID for admin check
        is_admin: Whether user is admin (if provided, skips check)
    """
    keyboard_rows = []
    
    # Row 1: Launch Mini App
    keyboard_rows.append([
        InlineKeyboardButton(
            text="💎 启动伍拾收银台",
            web_app=WebAppInfo(url=Config.get_miniapp_url("dashboard"))
        )
    ])
    
    # Row 2: Payment channels (跳轉到 MiniApp)
    keyboard_rows.append([
        InlineKeyboardButton(
            text="💳 支付宝",
            web_app=WebAppInfo(url=Config.get_miniapp_url("dashboard", "alipay"))
        ),
        InlineKeyboardButton(
            text="🍀 微信支付",
            web_app=WebAppInfo(url=Config.get_miniapp_url("dashboard", "wechat"))
        )
    ])
    
    # Row 3: Transaction records and Calculator (跳轉到 MiniApp)
    keyboard_rows.append([
        InlineKeyboardButton(
            text="📜 交易记录",
            web_app=WebAppInfo(url=Config.get_miniapp_url("history"))
        ),
        InlineKeyboardButton(
            text="🧮 汇率计算器",
            web_app=WebAppInfo(url=Config.get_miniapp_url("calculator"))
        )
    ])
    
    # Row 4: Wallet and Settings (跳轉到 MiniApp)
    keyboard_rows.append([
        InlineKeyboardButton(
            text="💰 我的钱包",
            web_app=WebAppInfo(url=Config.get_miniapp_url("wallet"))
        ),
        InlineKeyboardButton(
            text="⚙️ 个人设置",
            web_app=WebAppInfo(url=Config.get_miniapp_url("profile"))
        )
    ])
    
    # Row 5: Statistics (Bot 內顯示，因為 MiniApp 沒有)
    keyboard_rows.append([
        InlineKeyboardButton(
            text="📊 统计信息",
            callback_data="statistics"
        )
    ])
    
    # Row 6: Support and AI Assistant
    keyboard_rows.append([
        InlineKeyboardButton(
            text="💬 客服支持",
            url=Config.SUPPORT_URL
        ),
        InlineKeyboardButton(
            text="🤖 AI 助手",
            callback_data="ai_chat"
        )
    ])
    
    # Row 7: Admin Panel (僅管理員可見)
    if is_admin:
        keyboard_rows.append([
            InlineKeyboardButton(
                text="⚙️ 管理面板",
                callback_data="admin_panel"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    return keyboard


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """
    Returns the admin keyboard (only visible to admins).
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="👥 用户管理",
                callback_data="admin_users"
            ),
            InlineKeyboardButton(
                text="📊 系统统计",
                callback_data="admin_stats"
            )
        ],
        [
            InlineKeyboardButton(
                text="👤 添加管理员",
                callback_data="admin_add"
            ),
            InlineKeyboardButton(
                text="🚫 敏感词管理",
                callback_data="admin_words"
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ 群组审核",
                callback_data="admin_verify"
            ),
            InlineKeyboardButton(
                text="⚙️ 群组设置",
                callback_data="admin_group"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 返回主菜单",
                callback_data="main_menu"
            )
        ]
    ])
    
    return keyboard

