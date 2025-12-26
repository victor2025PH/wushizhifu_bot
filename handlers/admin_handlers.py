"""
Admin-related handlers (only visible to admins)
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from keyboards.main_kb import get_admin_keyboard, get_main_keyboard
from database.admin_repository import AdminRepository
from database.user_repository import UserRepository
from database.sensitive_words_repository import SensitiveWordsRepository
from database.group_repository import GroupRepository
from utils.text_utils import escape_markdown_v2, format_amount_markdown, format_number_markdown
from database.db import db

router = Router()
logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return AdminRepository.is_admin(user_id)


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Handle /admin command"""
    try:
        user_id = message.from_user.id
        
        if not is_admin(user_id):
            await message.answer("❌ 您不是管理員，無權限訪問此功能")
            return
        
        from utils.text_utils import format_separator
        
        separator = format_separator(30)
        
        text = (
            f"{separator}\n"
            f"  *⚙️ 管理员面板*\n"
            f"{separator}\n\n"
            
            f"*🎯 管理功能*\n"
            f"{separator}\n"
            f"👥 *用户管理*：查看和管理用户\n"
            f"📊 *系统统计*：查看系统数据\n"
            f"🚫 *敏感词管理*：管理敏感词\n"
            f"✅ *群组审核*：审核群组成员\n"
            f"⚙️ *群组设置*：管理群组配置\n"
            f"👤 *添加管理员*：添加新管理员\n\n"
            
            f"请选择要管理的功能："
        )
        
        await message.answer(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_admin_keyboard()
        )
        
        logger.info(f"Admin {user_id} accessed admin panel")
        
    except Exception as e:
        logger.error(f"Error in cmd_admin: {e}", exc_info=True)


@router.callback_query(F.data == "admin_panel")
async def callback_admin_panel(callback: CallbackQuery):
    """Handle admin panel entry"""
    try:
        user_id = callback.from_user.id
        
        if not is_admin(user_id):
            await callback.answer("❌ 您不是管理员，无权限访问此功能", show_alert=True)
            return
        
        from utils.text_utils import format_separator
        
        separator = format_separator(30)
        
        text = (
            f"{separator}\n"
            f"  *⚙️ 管理员面板*\n"
            f"{separator}\n\n"
            
            f"*🎯 管理功能*\n"
            f"{separator}\n"
            f"👥 *用户管理*：查看和管理用户\n"
            f"📊 *系统统计*：查看系统数据\n"
            f"🚫 *敏感词管理*：管理敏感词\n"
            f"✅ *群组审核*：审核群组成员\n"
            f"⚙️ *群组设置*：管理群组配置\n"
            f"👤 *添加管理员*：添加新管理员\n\n"
            
            f"请选择要管理的功能："
        )
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_admin_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_admin_panel: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data.startswith("admin_"))
async def callback_admin_menu(callback: CallbackQuery):
    """Handle admin menu callbacks"""
    try:
        user_id = callback.from_user.id
        
        if not is_admin(user_id):
            await callback.answer("❌ 您不是管理员", show_alert=True)
            return
        
        action = callback.data.split("_", 1)[1]
        
        if action == "panel":
            await callback_admin_panel(callback)
        elif action == "users":
            await handle_admin_users(callback)
        elif action == "stats":
            await handle_admin_stats(callback)
        elif action == "words":
            await handle_admin_words(callback)
        elif action == "verify":
            await handle_admin_verify(callback)
        elif action == "group":
            await handle_admin_group(callback)
        elif action == "add":
            await handle_admin_add(callback)
        
    except Exception as e:
        logger.error(f"Error in callback_admin_menu: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


async def handle_admin_users(callback: CallbackQuery):
    """Handle admin users management"""
    from database.db import db
    from datetime import datetime
    from utils.text_utils import format_number_markdown, format_separator
    
    # Get statistics
    cursor = db.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor = db.execute("SELECT COUNT(*) FROM users WHERE status = 'active'")
    active_users = cursor.fetchone()[0]
    
    # Get today's new users
    cursor = db.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE('now')")
    today_new = cursor.fetchone()[0]
    
    # Get VIP users
    cursor = db.execute("SELECT COUNT(*) FROM users WHERE vip_level > 0")
    vip_users = cursor.fetchone()[0]
    
    # Get recent users
    cursor = db.execute("""
        SELECT user_id, username, first_name, vip_level, created_at 
        FROM users 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    recent_users = cursor.fetchall()
    
    separator = format_separator(30)
    total_users_str = format_number_markdown(total_users)
    active_users_str = format_number_markdown(active_users)
    today_new_str = format_number_markdown(today_new)
    vip_users_str = format_number_markdown(vip_users)
    
    text = (
        f"{separator}\n"
        f"  *👥 用户管理*\n"
        f"{separator}\n\n"
        
        f"*📊 用户统计*\n"
        f"{separator}\n"
        f"总用户数：{total_users_str}\n"
        f"活跃用户：{active_users_str}\n"
        f"今日新增：{today_new_str}\n"
        f"VIP用户：{vip_users_str}\n\n"
        
        f"*📋 最近注册用户（前10名）*\n"
        f"{separator}\n"
    )
    
    if not recent_users:
        text += "暂无用户数据"
    else:
        for idx, user in enumerate(recent_users[:10], 1):
            # Fix: sqlite3.Row objects use column access, not .get()
            username = user['username'] if user['username'] else '无'
            username_display = f"@{username}" if username != '无' else "无"
            first_name = user['first_name'] if user['first_name'] else ''
            vip_level = user['vip_level'] if user['vip_level'] is not None else 0
            user_id = user['user_id']
            created_at = user['created_at'][:10] if user['created_at'] else 'N/A'
            
            username_escaped = escape_markdown_v2(username_display)
            first_name_escaped = escape_markdown_v2(first_name) if first_name else "未设置"
            vip_text = f"VIP{vip_level}" if vip_level > 0 else "普通"
            user_id_str = format_number_markdown(user_id)
            created_at_escaped = escape_markdown_v2(created_at)
            
            text += (
                f"{format_number_markdown(idx)}\\. {username_escaped} \\(ID: {user_id_str}\\)\n"
                f"   姓名：{first_name_escaped} \\| {escape_markdown_v2(vip_text)} \\| {created_at_escaped}\n\n"
            )
    
    text += "\n💡 更多功能开发中\\.\\.\\."
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 搜索用户", callback_data="admin_user_search"),
            InlineKeyboardButton(text="📊 用户报表", callback_data="admin_user_report")
        ],
        [
            InlineKeyboardButton(text="🔙 返回管理面板", callback_data="admin_panel")
        ]
    ])
    
    await callback.message.edit_text(
        text=text,
        parse_mode="MarkdownV2",
        reply_markup=keyboard
    )
    await callback.answer()


async def handle_admin_stats(callback: CallbackQuery):
    """Handle admin statistics"""
    from database.db import db
    from database.transaction_repository import TransactionRepository
    from database.referral_repository import ReferralRepository
    from datetime import datetime, timedelta
    from utils.text_utils import format_separator
    
    # Get transaction statistics
    cursor = db.execute("SELECT COUNT(*) FROM transactions")
    total_transactions = cursor.fetchone()[0]
    
    cursor = db.execute("SELECT COUNT(*) FROM transactions WHERE status = 'paid'")
    paid_transactions = cursor.fetchone()[0]
    
    cursor = db.execute("SELECT SUM(amount) FROM transactions WHERE status = 'paid'")
    total_amount = cursor.fetchone()[0] or 0
    
    # Get today's transactions
    cursor = db.execute("""
        SELECT COUNT(*), COALESCE(SUM(amount), 0) 
        FROM transactions 
        WHERE DATE(created_at) = DATE('now') AND status = 'paid'
    """)
    today_result = cursor.fetchone()
    today_transactions = today_result[0] or 0
    today_amount = float(today_result[1] or 0)
    
    # Get yesterday's transactions
    cursor = db.execute("""
        SELECT COUNT(*), COALESCE(SUM(amount), 0) 
        FROM transactions 
        WHERE DATE(created_at) = DATE('now', '-1 day') AND status = 'paid'
    """)
    yesterday_result = cursor.fetchone()
    yesterday_transactions = yesterday_result[0] or 0
    
    # Get channel statistics
    cursor = db.execute("""
        SELECT payment_channel, COUNT(*) as count 
        FROM transactions 
        WHERE status = 'paid' 
        GROUP BY payment_channel
    """)
    channel_stats = cursor.fetchall()
    
    # Get user statistics
    cursor = db.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor = db.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE('now')")
    today_new_users = cursor.fetchone()[0]
    
    # Get referral statistics
    cursor = db.execute("SELECT COUNT(*) FROM referrals WHERE status = 'rewarded'")
    successful_invites = cursor.fetchone()[0]
    
    cursor = db.execute("SELECT COALESCE(SUM(total_rewards), 0) FROM referral_codes")
    total_referral_rewards = float(cursor.fetchone()[0] or 0)
    
    separator = format_separator(30)
    total_transactions_str = format_number_markdown(total_transactions)
    paid_transactions_str = format_number_markdown(paid_transactions)
    success_rate = (paid_transactions / total_transactions * 100) if total_transactions > 0 else 0
    success_rate_str = format_number_markdown(success_rate, decimal_places=1)
    total_amount_str = format_amount_markdown(total_amount)
    today_transactions_str = format_number_markdown(today_transactions)
    today_amount_str = format_amount_markdown(today_amount)
    yesterday_transactions_str = format_number_markdown(yesterday_transactions)
    total_users_str = format_number_markdown(total_users)
    today_new_users_str = format_number_markdown(today_new_users)
    successful_invites_str = format_number_markdown(successful_invites)
    total_referral_rewards_str = format_amount_markdown(total_referral_rewards, currency="USDT")
    
    text = (
        f"{separator}\n"
        f"  *📊 系统统计*\n"
        f"{separator}\n\n"
        
        f"*💎 核心指标*\n"
        f"{separator}\n"
        f"总交易数：{total_transactions_str} 笔\n"
        f"成功交易：{paid_transactions_str} 笔 \\({success_rate_str}%\\)\n"
        f"总交易额：{total_amount_str}\n"
        f"今日交易：{today_transactions_str} 笔 / {today_amount_str}\n\n"
        
        f"*📈 交易趋势*\n"
        f"{separator}\n"
        f"今日：{today_transactions_str} 笔\n"
        f"昨日：{yesterday_transactions_str} 笔\n\n"
    )
    
    if channel_stats:
        text += f"*💳 支付渠道统计*\n"
        text += f"{separator}\n"
        # Fix: sqlite3.Row objects use column access
        total_paid = sum(stat['count'] for stat in channel_stats)
        for stat in channel_stats:
            channel = stat['payment_channel']
            count = stat['count']
            percentage = (count / total_paid * 100) if total_paid > 0 else 0
            channel_text = "支付宝" if channel == "alipay" else "微信支付"
            count_str = format_number_markdown(count)
            percentage_str = format_number_markdown(percentage, decimal_places=1)
            text += f"{escape_markdown_v2(channel_text)}：{count_str} 笔 \\({percentage_str}%\\)\n"
        text += "\n"
    
    text += (
        f"*👥 用户统计*\n"
        f"{separator}\n"
        f"总用户：{total_users_str}\n"
        f"今日新增：{today_new_users_str}\n\n"
        
        f"*🎁 分享活动统计*\n"
        f"{separator}\n"
        f"成功邀请：{successful_invites_str} 人\n"
        f"累计奖励：{total_referral_rewards_str}\n\n"
        
        f"💡 更多详细报表功能开发中\\.\\.\\."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 时间统计", callback_data="admin_stats_time"),
            InlineKeyboardButton(text="📊 详细报表", callback_data="admin_stats_detail")
        ],
        [
            InlineKeyboardButton(text="🔙 返回管理面板", callback_data="admin_panel")
        ]
    ])
    
    await callback.message.edit_text(
        text=text,
        parse_mode="MarkdownV2",
        reply_markup=keyboard
    )
    await callback.answer()


async def handle_admin_words(callback: CallbackQuery):
    """Handle sensitive words management"""
    from utils.text_utils import format_separator
    
    words = SensitiveWordsRepository.get_words()
    
    separator = format_separator(30)
    words_count_str = format_number_markdown(len(words))
    
    if not words:
        text = (
            f"{separator}\n"
            f"  *🚫 敏感词管理*\n"
            f"{separator}\n\n"
            f"暂无敏感词\n\n"
            f"请使用 `/addword <词语> [action]` 添加\n"
            f"动作：warn \\(警告\\)、delete \\(删除\\)、ban \\(封禁\\)"
        )
    else:
        text = (
            f"{separator}\n"
            f"  *🚫 敏感词管理*\n"
            f"{separator}\n\n"
            f"*当前敏感词列表 \\(共 {words_count_str} 个\\)：*\n\n"
        )
        
        action_map = {"warn": "警告", "delete": "删除", "ban": "封禁"}
        
        for idx, word in enumerate(words[:15], 1):
            action_text = action_map.get(word['action'], word['action'])
            word_escaped = escape_markdown_v2(word['word'])
            action_escaped = escape_markdown_v2(action_text)
            text += f"{format_number_markdown(idx)}\\. `{word_escaped}` \\- {action_escaped}\n"
        
        if len(words) > 15:
            remaining = format_number_markdown(len(words) - 15)
            text += f"\n还有 {remaining} 个\\.\\.\\."
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ 添加敏感词", callback_data="admin_word_add"),
            InlineKeyboardButton(text="📋 导出列表", callback_data="admin_word_export")
        ],
        [
            InlineKeyboardButton(text="🔙 返回管理面板", callback_data="admin_panel")
        ]
    ])
    
    await callback.message.edit_text(
        text=text,
        parse_mode="MarkdownV2",
        reply_markup=keyboard
    )
    await callback.answer()


async def handle_admin_verify(callback: CallbackQuery):
    """Handle group verification management"""
    from database.db import db
    from utils.text_utils import format_separator, format_number_markdown
    
    cursor = db.execute("""
        SELECT gm.*, g.group_title 
        FROM group_members gm
        JOIN groups g ON gm.group_id = g.group_id
        WHERE gm.status = 'pending'
        ORDER BY gm.joined_at ASC
        LIMIT 10
    """)
    
    pending = cursor.fetchall()
    
    separator = format_separator(30)
    pending_count_str = format_number_markdown(len(pending))
    
    if not pending:
        text = (
            f"{separator}\n"
            f"  *✅ 群组审核*\n"
            f"{separator}\n\n"
            f"暂无待审核成员\n\n"
            f"所有成员已审核完成"
        )
    else:
        text = (
            f"{separator}\n"
            f"  *✅ 群组审核*\n"
            f"{separator}\n\n"
            f"*待审核成员 \\(共 {pending_count_str} 人\\)：*\n\n"
        )
        
        for idx, member in enumerate(pending[:10], 1):
            # Fix: sqlite3.Row objects use column access, not .get()
            user_id = member['user_id']
            group_title = member['group_title'] if member['group_title'] else f"群组 {member['group_id']}"
            joined_at = member['joined_at'][:16] if member['joined_at'] else 'N/A'
            
            user_id_str = format_number_markdown(user_id)
            group_title_escaped = escape_markdown_v2(str(group_title))
            joined_at_escaped = escape_markdown_v2(joined_at)
            
            text += (
                f"{format_number_markdown(idx)}\\. 用户ID：{user_id_str}\n"
                f"   群组：{group_title_escaped}\n"
                f"   加入时间：{joined_at_escaped}\n\n"
            )
        
        text += "💡 点击下方按钮进行审核操作"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    if pending:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="✅ 全部通过", callback_data="admin_verify_all_approve"),
            InlineKeyboardButton(text="❌ 全部拒绝", callback_data="admin_verify_all_reject")
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 返回管理面板", callback_data="admin_panel")
    ])
    
    await callback.message.edit_text(
        text=text,
        parse_mode="MarkdownV2",
        reply_markup=keyboard
    )
    await callback.answer()


async def handle_admin_group(callback: CallbackQuery):
    """Handle group settings"""
    from database.db import db
    from utils.text_utils import format_separator, format_number_markdown
    
    # Get all groups
    cursor = db.execute("""
        SELECT g.*, 
               COUNT(DISTINCT gm.user_id) as member_count,
               COUNT(DISTINCT CASE WHEN gm.status = 'pending' THEN gm.user_id END) as pending_count
        FROM groups g
        LEFT JOIN group_members gm ON g.group_id = gm.group_id
        GROUP BY g.group_id
        ORDER BY g.created_at DESC
        LIMIT 10
    """)
    
    groups = cursor.fetchall()
    
    separator = format_separator(30)
    groups_count_str = format_number_markdown(len(groups))
    
    text = (
        f"{separator}\n"
        f"  *⚙️ 群组设置*\n"
        f"{separator}\n\n"
    )
    
    if not groups:
        text += "暂无管理的群组\n\n请先添加群组到管理系统"
    else:
        text += f"*已管理群组 \\(共 {groups_count_str} 个\\)：*\n\n"
        
        for idx, group in enumerate(groups[:10], 1):
            # Fix: sqlite3.Row objects use column access, not .get()
            group_id = group['group_id']
            group_title = group['group_title'] if group['group_title'] else f"群组 {group_id}"
            verification_enabled = group['verification_enabled'] if group['verification_enabled'] is not None else 0
            member_count = group['member_count'] if group['member_count'] is not None else 0
            pending_count = group['pending_count'] if group['pending_count'] is not None else 0
            
            group_title_escaped = escape_markdown_v2(str(group_title))
            verification_text = "已开启" if verification_enabled else "已关闭"
            member_count_str = format_number_markdown(member_count)
            pending_count_str = format_number_markdown(pending_count)
            
            text += (
                f"{format_number_markdown(idx)}\\. {group_title_escaped}\n"
                f"   审核：{escape_markdown_v2(verification_text)} \\| "
                f"成员：{member_count_str} \\| "
                f"待审核：{pending_count_str}\n\n"
            )
        
        text += "💡 点击下方按钮管理群组设置"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ 添加群组", callback_data="admin_group_add"),
            InlineKeyboardButton(text="📋 群组列表", callback_data="admin_group_list")
        ],
        [
            InlineKeyboardButton(text="🔙 返回管理面板", callback_data="admin_panel")
        ]
    ])
    
    await callback.message.edit_text(
        text=text,
        parse_mode="MarkdownV2",
        reply_markup=keyboard
    )
    await callback.answer()


async def handle_admin_add(callback: CallbackQuery):
    """Handle add admin"""
    from database.db import db
    from utils.text_utils import format_separator, format_number_markdown
    
    # Get all admins
    cursor = db.execute("""
        SELECT a.*, u.username, u.first_name 
        FROM admins a
        LEFT JOIN users u ON a.user_id = u.user_id
        WHERE a.status = 'active'
        ORDER BY a.added_at DESC
    """)
    
    admins = cursor.fetchall()
    
    separator = format_separator(30)
    admins_count_str = format_number_markdown(len(admins))
    
    text = (
        f"{separator}\n"
        f"  *👤 添加管理员*\n"
        f"{separator}\n\n"
        
        f"*📋 当前管理员 \\(共 {admins_count_str} 人\\)：*\n\n"
    )
    
    if not admins:
        text += "暂无管理员"
    else:
        for idx, admin in enumerate(admins[:10], 1):
            # Fix: sqlite3.Row objects use column access, not .get()
            user_id = admin['user_id']
            username = admin['username'] if admin['username'] else '无'
            username_display = f"@{username}" if username != '无' else "无"
            first_name = admin['first_name'] if admin['first_name'] else ''
            role = admin['role'] if admin['role'] else 'admin'
            added_at = admin['added_at'][:10] if admin['added_at'] else 'N/A'
            
            username_escaped = escape_markdown_v2(username_display)
            first_name_escaped = escape_markdown_v2(first_name) if first_name else "未设置"
            role_escaped = escape_markdown_v2(role)
            user_id_str = format_number_markdown(user_id)
            added_at_escaped = escape_markdown_v2(added_at)
            
            text += (
                f"{format_number_markdown(idx)}\\. {username_escaped} \\(ID: {user_id_str}\\)\n"
                f"   姓名：{first_name_escaped} \\| 角色：{role_escaped} \\| 添加时间：{added_at_escaped}\n\n"
            )
    
    text += (
        f"\n{separator}\n"
        f"*添加方式*\n"
        f"{separator}\n"
        f"请使用命令：\n"
        f"`/addadmin <user_id>`\n\n"
        f"例如：\n"
        f"`/addadmin 123456789`\n\n"
        f"💡 界面添加功能开发中\\.\\.\\."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ 添加管理员", callback_data="admin_add_new"),
            InlineKeyboardButton(text="🗑️ 删除管理员", callback_data="admin_remove")
        ],
        [
            InlineKeyboardButton(text="🔙 返回管理面板", callback_data="admin_panel")
        ]
    ])
    
    await callback.message.edit_text(
        text=text,
        parse_mode="MarkdownV2",
        reply_markup=keyboard
    )
    await callback.answer()


@router.message(Command("addadmin"))
async def cmd_add_admin(message: Message):
    """Add admin command"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ 您不是管理員，無權限執行此操作")
            return
        
        args = message.text.split()
        if len(args) < 2:
            await message.answer("❌ 請提供用戶ID\n格式：`/addadmin <user_id>`", parse_mode="MarkdownV2")
            return
        
        try:
            user_id = int(args[1])
            if AdminRepository.add_admin(user_id, added_by=message.from_user.id):
                await message.answer(f"✅ 已添加管理員：{user_id}")
            else:
                await message.answer(f"❌ 添加失敗（可能已是管理員）")
        except ValueError:
            await message.answer("❌ 無效的用戶ID")
            
    except Exception as e:
        logger.error(f"Error in cmd_add_admin: {e}", exc_info=True)


@router.message(Command("addword"))
async def cmd_add_word(message: Message):
    """Add sensitive word command"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ 您不是管理員，無權限執行此操作")
            return
        
        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            await message.answer("❌ 請提供敏感詞\n格式：`/addword <詞語> [action]`\n動作：warn, delete, ban", parse_mode="MarkdownV2")
            return
        
        word = args[1]
        action = args[2] if len(args) > 2 else "warn"
        
        if action not in ["warn", "delete", "ban"]:
            action = "warn"
        
        if SensitiveWordsRepository.add_word(None, word, action, message.from_user.id):
            await message.answer(f"✅ 已添加敏感詞：`{word}` (動作：{action})", parse_mode="MarkdownV2")
        else:
            await message.answer("❌ 添加失敗（可能已存在）")
            
    except Exception as e:
        logger.error(f"Error in cmd_add_word: {e}", exc_info=True)


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery):
    """Return to main menu"""
    from services.message_service import MessageService
    from services.user_service import UserService
    
    try:
        user = callback.from_user
        is_new = UserService.is_new_user(user.id)
        welcome_text = MessageService.generate_welcome_message(user, is_new)
        
        is_admin = AdminRepository.is_admin(user.id)
        
        await callback.message.edit_text(
            text=welcome_text,
            parse_mode="MarkdownV2",
            reply_markup=get_main_keyboard(user_id=user.id, is_admin=is_admin)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_main_menu: {e}", exc_info=True)
        await callback.answer("❌ 系統錯誤", show_alert=True)

