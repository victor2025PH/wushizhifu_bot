"""
Text utilities for message formatting and escaping
"""
import re


def escape_markdown_v2(text: str) -> str:
    """
    Escape special characters for MarkdownV2 format.
    Characters that need escaping: _ * [ ] ( ) ~ ` > # + - = | { } . !
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text safe for MarkdownV2
    """
    if not text:
        return ""
    special_chars = r"_*[]()~`>#+-=|{}.!"
    escaped = ""
    for char in text:
        if char in special_chars:
            escaped += "\\" + char
        else:
            escaped += char
    return escaped


def format_amount_markdown(amount: float, currency: str = "¥", decimal_places: int = 2) -> str:
    """
    Format amount for MarkdownV2 with proper escaping.
    
    Args:
        amount: Amount to format
        currency: Currency symbol (default: "¥")
        decimal_places: Number of decimal places (default: 2)
        
    Returns:
        Formatted and escaped string (e.g., "¥1\\,000\\.50")
    """
    if amount is None:
        amount = 0.0
    
    # Format with thousand separators and decimals
    formatted = f"{amount:,.{decimal_places}f}"
    
    # Escape MarkdownV2 special characters
    escaped = escape_markdown_v2(formatted)
    
    return f"{currency}{escaped}"


def format_number_markdown(number: float, decimal_places: int = 0) -> str:
    """
    Format number for MarkdownV2 with proper escaping.
    
    Args:
        number: Number to format
        decimal_places: Number of decimal places (default: 0)
        
    Returns:
        Formatted and escaped string (e.g., "1\\,234" or "1\\,234\\.56")
    """
    if number is None:
        number = 0.0
    
    if decimal_places == 0:
        formatted = f"{number:,.0f}"
    else:
        formatted = f"{number:,.{decimal_places}f}"
    
    # Escape MarkdownV2 special characters
    return escape_markdown_v2(formatted)


def format_percentage_markdown(value: float, decimal_places: int = 2) -> str:
    """
    Format percentage for MarkdownV2 with proper escaping.
    
    Args:
        value: Percentage value (e.g., 0.6 for 0.6%)
        decimal_places: Number of decimal places (default: 2)
        
    Returns:
        Formatted and escaped string (e.g., "0\\.60%")
    """
    if value is None:
        value = 0.0
    
    formatted = f"{value:.{decimal_places}f}%"
    
    # Escape MarkdownV2 special characters
    return escape_markdown_v2(formatted)


def format_separator(length: int = 30, char: str = "-") -> str:
    """
    Format separator line for MarkdownV2.
    
    Args:
        length: Length of separator (default: 30)
        char: Character to use (default: "-", will be escaped)
        
    Returns:
        Escaped separator string
    """
    separator = char * length
    return escape_markdown_v2(separator)


def get_user_display_name(user) -> str:
    """
    Get user's display name for greeting.
    Priority: first_name + last_name > first_name > username > "尊貴的客戶"
    
    Args:
        user: Telegram User object
        
    Returns:
        Escaped display name for MarkdownV2
    """
    if user.first_name:
        name = user.first_name
        if user.last_name:
            name += " " + user.last_name
        return escape_markdown_v2(name)
    elif user.username:
        return escape_markdown_v2(user.username)
    else:
        return "尊貴的客戶"


def format_user_info(user) -> dict:
    """
    Format user information into a structured dict.
    
    Args:
        user: Telegram User object
        
    Returns:
        Dictionary with formatted user information
    """
    return {
        "id": user.id,
        "username": user.username if user.username else None,
        "first_name": user.first_name if user.first_name else None,
        "last_name": user.last_name if user.last_name else None,
        "full_name": f"{user.first_name} {user.last_name}".strip() if user.first_name else None,
        "display_name": get_user_display_name(user),
        "is_premium": getattr(user, "is_premium", False),
        "language_code": getattr(user, "language_code", None)
    }

