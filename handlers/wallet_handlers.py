"""
Wallet-related handlers
"""
import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.main_kb import get_main_keyboard
from database.admin_repository import AdminRepository
from database.user_repository import UserRepository
from database.transaction_repository import TransactionRepository
from services.transaction_service import TransactionService
from database.db import db
from utils.text_utils import escape_markdown_v2

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "wallet")
async def callback_wallet(callback: CallbackQuery):
    """Handle wallet menu"""
    try:
        user_id = callback.from_user.id
        
        # Get user info
        user = UserRepository.get_user(user_id)
        if not user:
            await callback.answer("❌ 用户信息不存在", show_alert=True)
            return
        
        # Calculate balance from transactions (if balance field doesn't exist)
        # For now, we'll calculate from completed transactions
        cursor = db.execute("""
            SELECT transaction_type, actual_amount 
            FROM transactions 
            WHERE user_id = ? AND status = 'paid'
        """, (user_id,))
        transactions = cursor.fetchall()
        
        balance = 0.0
        for trans in transactions:
            if trans['transaction_type'] == 'receive':
                balance += float(trans['actual_amount'])
            elif trans['transaction_type'] == 'pay':
                balance -= float(trans['actual_amount'])
        
        # Get today's statistics
        today = datetime.now().strftime("%Y-%m-%d")
        cursor = db.execute("""
            SELECT transaction_type, actual_amount 
            FROM transactions 
            WHERE user_id = ? AND status = 'paid' 
            AND DATE(created_at) = DATE('now')
        """, (user_id,))
        today_transactions = cursor.fetchall()
        
        today_receive = sum(float(t['actual_amount']) for t in today_transactions 
                           if t['transaction_type'] == 'receive')
        today_pay = sum(float(t['actual_amount']) for t in today_transactions 
                       if t['transaction_type'] == 'pay')
        
        text = (
            "*💰 我的钱包*\n\n"
            f"总余额：`{balance:,.2f}` USDT\n"
            f"可用余额：`{balance:,.2f}` USDT\n"
            f"冻结余额：`0.00` USDT\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "*今日统计*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💳 充值：¥{today_receive:,.2f}\n"
            f"📤 提现：`{today_pay:,.2f}` USDT\n\n"
            f"📊 累计交易：{user.get('total_transactions', 0)} 笔\n"
            f"💰 累计金额：¥{user.get('total_amount', 0):,.2f}"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 充值", callback_data="wallet_deposit"),
                InlineKeyboardButton(text="📤 提现", callback_data="wallet_withdraw")
            ],
            [
                InlineKeyboardButton(text="📜 交易记录", callback_data="transactions"),
                InlineKeyboardButton(text="📊 钱包明细", callback_data="wallet_details")
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
        logger.error(f"Error in callback_wallet: {e}", exc_info=True)
        await callback.answer("❌ 获取钱包信息失败，请稍后再试", show_alert=True)


@router.callback_query(F.data == "wallet_deposit")
async def callback_wallet_deposit(callback: CallbackQuery):
    """Handle wallet deposit"""
    try:
        text = (
            "*💳 充值*\n\n"
            "请选择支付通道："
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 支付宝充值", callback_data="pay_ali"),
                InlineKeyboardButton(text="🍀 微信充值", callback_data="pay_wechat")
            ],
            [
                InlineKeyboardButton(text="🔙 返回钱包", callback_data="wallet")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_wallet_deposit: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data == "wallet_withdraw")
async def callback_wallet_withdraw(callback: CallbackQuery):
    """Handle wallet withdraw"""
    try:
        user_id = callback.from_user.id
        user = UserRepository.get_user(user_id)
        
        # Calculate balance
        cursor = db.execute("""
            SELECT transaction_type, actual_amount 
            FROM transactions 
            WHERE user_id = ? AND status = 'paid'
        """, (user_id,))
        transactions = cursor.fetchall()
        
        balance = sum(float(t['actual_amount']) for t in transactions 
                     if t['transaction_type'] == 'receive')
        balance -= sum(float(t['actual_amount']) for t in transactions 
                      if t['transaction_type'] == 'pay')
        
        if balance <= 0:
            text = (
                "*📤 提现*\n\n"
                "❌ 余额不足，无法提现\n\n"
                f"当前余额：`{balance:,.2f}` USDT"
            )
        else:
            text = (
                "*📤 提现*\n\n"
                f"当前可用余额：`{balance:,.2f}` USDT\n\n"
                "请输入提现金额（USDT）：\n"
                "最小提现金额：10 USDT\n"
                "最大提现金额：无限制"
            )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 返回钱包", callback_data="wallet")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_wallet_withdraw: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data == "wallet_details")
async def callback_wallet_details(callback: CallbackQuery):
    """Handle wallet details"""
    try:
        user_id = callback.from_user.id
        transactions = TransactionRepository.get_user_transactions(user_id, limit=20)
        
        if not transactions:
            text = "*📊 钱包明细*\n\n暂无交易记录"
        else:
            text = "*📊 钱包明细*\n\n*最近 10 笔交易：*\n\n"
            
            for trans in transactions[:10]:
                status_icon = "✅" if trans['status'] == 'paid' else "⏳" if trans['status'] == 'pending' else "❌"
                type_icon = "💳" if trans['transaction_type'] == 'receive' else "📤"
                amount_sign = "+" if trans['transaction_type'] == 'receive' else "-"
                
                text += (
                    f"{status_icon} {type_icon} {amount_sign}¥{trans['actual_amount']:,.2f}\n"
                    f"   {trans['created_at']} | `{trans['order_id'][:16]}...`\n\n"
                )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📜 查看全部记录", callback_data="transactions")
            ],
            [
                InlineKeyboardButton(text="🔙 返回钱包", callback_data="wallet")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_wallet_details: {e}", exc_info=True)
        await callback.answer("❌ 获取钱包明细失败，请稍后再试", show_alert=True)

