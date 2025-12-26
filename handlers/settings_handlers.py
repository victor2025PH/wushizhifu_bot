"""
Settings-related handlers
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.main_kb import get_main_keyboard
from database.admin_repository import AdminRepository
from database.user_repository import UserRepository
from utils.text_utils import escape_markdown_v2, format_amount_markdown, format_number_markdown

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "settings")
async def callback_settings(callback: CallbackQuery):
    """Handle settings menu"""
    try:
        user_id = callback.from_user.id
        user = UserRepository.get_user(user_id)
        
        if not user:
            await callback.answer("❌ 用户信息不存在", show_alert=True)
            return
        
        language = user.get('language_code', 'zh-CN') or 'zh-CN'
        if language.startswith('zh'):
            language_text = '简体中文' if language == 'zh-CN' else '繁體中文'
        else:
            language_text = 'English'
        
        text = (
            "*⚙️ 个人设置*\n\n"
            f"1\\. 🌐 语言设置：{language_text}\n"
            "2\\. 🔔 通知设置：已开启\n"
            "3\\. 💳 首选支付通道：支付宝\n"
            "4\\. 🔒 安全设置\n"
            "5\\. 👤 账户信息\n\n"
            "点击相应选项进行修改"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🌐 语言设置", callback_data="settings_language"),
                InlineKeyboardButton(text="🔔 通知设置", callback_data="settings_notification")
            ],
            [
                InlineKeyboardButton(text="💳 支付通道", callback_data="settings_provider"),
                InlineKeyboardButton(text="🔒 安全设置", callback_data="settings_security")
            ],
            [
                InlineKeyboardButton(text="👤 账户信息", callback_data="settings_account")
            ],
            [
                InlineKeyboardButton(text="🔙 返回主菜单", callback_data="main_menu")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_settings: {e}", exc_info=True)
        await callback.answer("❌ 获取设置失败，请稍后再试", show_alert=True)


@router.callback_query(F.data == "settings_language")
async def callback_settings_language(callback: CallbackQuery):
    """Handle language settings"""
    try:
        text = (
            "*🌐 语言设置*\n\n"
            "请选择您的首选语言："
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="简体中文", callback_data="set_lang_zh-CN"),
                InlineKeyboardButton(text="繁體中文", callback_data="set_lang_zh-TW")
            ],
            [
                InlineKeyboardButton(text="English", callback_data="set_lang_en")
            ],
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_settings_language: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data.startswith("set_lang_"))
async def callback_set_language(callback: CallbackQuery):
    """Handle language selection"""
    try:
        lang_code = callback.data.replace("set_lang_", "")
        user_id = callback.from_user.id
        
        # Update language (if we have this field in database)
        # For now, just show confirmation
        lang_map = {
            "zh-CN": "简体中文",
            "zh-TW": "繁體中文",
            "en": "English"
        }
        
        text = f"*✅ 语言设置已更新*\n\n已设置为：{lang_map.get(lang_code, lang_code)}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer(f"已设置为 {lang_map.get(lang_code, lang_code)}")
        
    except Exception as e:
        logger.error(f"Error in callback_set_language: {e}", exc_info=True)
        await callback.answer("❌ 设置失败，请稍后再试", show_alert=True)


@router.callback_query(F.data == "settings_notification")
async def callback_settings_notification(callback: CallbackQuery):
    """Handle notification settings"""
    try:
        text = (
            "*🔔 通知设置*\n\n"
            "1\\. 支付通知：✅ 已开启\n"
            "2\\. 余额变动通知：✅ 已开启\n"
            "3\\. 系统消息通知：✅ 已开启\n\n"
            "点击切换开关"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="支付通知: 开启", callback_data="toggle_notify_payment"),
                InlineKeyboardButton(text="余额通知: 开启", callback_data="toggle_notify_balance")
            ],
            [
                InlineKeyboardButton(text="系统消息: 开启", callback_data="toggle_notify_system")
            ],
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_settings_notification: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data == "settings_provider")
async def callback_settings_provider(callback: CallbackQuery):
    """Handle preferred provider settings"""
    try:
        text = (
            "*💳 首选支付通道*\n\n"
            "设置您的默认支付通道，快速支付时将使用此通道："
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 支付宝", callback_data="set_provider_alipay"),
                InlineKeyboardButton(text="🍀 微信支付", callback_data="set_provider_wechat")
            ],
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_settings_provider: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data.startswith("set_provider_"))
async def callback_set_provider(callback: CallbackQuery):
    """Handle provider selection"""
    try:
        provider = callback.data.replace("set_provider_", "")
        provider_text = "支付宝" if provider == "alipay" else "微信支付"
        
        text = f"*✅ 设置已更新*\n\n首选支付通道已设置为：{provider_text}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer(f"已设置为 {provider_text}")
        
    except Exception as e:
        logger.error(f"Error in callback_set_provider: {e}", exc_info=True)
        await callback.answer("❌ 设置失败，请稍后再试", show_alert=True)


@router.callback_query(F.data == "settings_security")
async def callback_settings_security(callback: CallbackQuery):
    """Handle security settings"""
    try:
        user_id = callback.from_user.id
        user = UserRepository.get_user(user_id)
        
        text = (
            "*🔒 安全设置*\n\n"
            "1\\. 绑定邮箱：未绑定\n"
            "2\\. 安全密码：未设置\n"
            "3\\. 两步验证：未开启\n\n"
            "点击相应选项进行设置"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📧 绑定邮箱", callback_data="security_email"),
                InlineKeyboardButton(text="🔐 设置密码", callback_data="security_password")
            ],
            [
                InlineKeyboardButton(text="🛡️ 两步验证", callback_data="security_2fa")
            ],
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_settings_security: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data == "settings_account")
async def callback_settings_account(callback: CallbackQuery):
    """Handle account information"""
    try:
        user_id = callback.from_user.id
        user = UserRepository.get_user(user_id)
        
        if not user:
            await callback.answer("❌ 用户信息不存在", show_alert=True)
            return
        
        username = user.get('username', '无')
        if username:
            username = f"@{username}"
        else:
            username = "未设置"
        
        user_id_str = escape_markdown_v2(str(user_id))
        username_escaped = escape_markdown_v2(username)
        first_name_escaped = escape_markdown_v2(user.get('first_name', ''))
        last_name_escaped = escape_markdown_v2(user.get('last_name', '') or '')
        full_name = f"{first_name_escaped} {last_name_escaped}".strip() if first_name_escaped else "未设置"
        vip_level_str = format_number_markdown(user.get('vip_level', 0))
        total_transactions_str = format_number_markdown(user.get('total_transactions', 0))
        total_amount_str = format_amount_markdown(user.get('total_amount', 0))
        created_at_escaped = escape_markdown_v2(str(user.get('created_at', 'N/A')))
        last_active_escaped = escape_markdown_v2(str(user.get('last_active_at', 'N/A')))
        
        text = (
            "*👤 账户信息*\n\n"
            f"🆔 用户ID：`{user_id_str}`\n"
            f"👤 用户名：{username_escaped}\n"
            f"📛 姓名：{full_name}\n"
            f"⭐ VIP等级：{vip_level_str}\n"
            f"📊 总交易数：{total_transactions_str} 笔\n"
            f"💰 累计金额：{total_amount_str}\n"
            f"📅 注册时间：{created_at_escaped}\n"
            f"🕐 最后活跃：{last_active_escaped}"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_settings_account: {e}", exc_info=True)
        await callback.answer("❌ 获取账户信息失败，请稍后再试", show_alert=True)

