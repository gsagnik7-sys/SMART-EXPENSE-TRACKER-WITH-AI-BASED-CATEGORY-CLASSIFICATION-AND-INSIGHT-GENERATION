"""
utils.py
--------
Shared helper utilities used across the project.
"""

import re
from typing import Optional


def format_currency(amount: float, symbol: str = "₹") -> str:
    """Format a float as a currency string. e.g. 1234.5 → '₹1,234.50'"""
    try:
        return f"{symbol}{amount:,.2f}"
    except (TypeError, ValueError):
        return f"{symbol}0.00"


def validate_amount(value: str) -> Optional[float]:
    """
    Parse and validate an amount string.

    Returns:
        Float if valid and > 0, else None.
    """
    value = value.strip().replace(",", "")
    try:
        amount = float(value)
        if amount <= 0:
            return None
        return round(amount, 2)
    except ValueError:
        return None


def sanitize_text(text: str, max_len: int = 100) -> str:
    """
    Clean a text input: strip whitespace, remove special chars, cap length.

    Args:
        text:    Raw input string
        max_len: Maximum allowed length

    Returns:
        Sanitized string
    """
    text = text.strip()
    # Keep letters, digits, spaces, hyphens, dots, slashes
    text = re.sub(r"[^\w\s\-\./]", "", text)
    return text[:max_len]


def truncate(text: str, max_len: int = 25) -> str:
    """Truncate text to max_len with ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 1] + "…"


CATEGORY_COLORS = {
    "Food":          "#FF6B6B",
    "Travel":        "#4ECDC4",
    "Shopping":      "#45B7D1",
    "Entertainment": "#96CEB4",
    "Health":        "#FFEAA7",
    "Utilities":     "#DDA0DD",
    "Education":     "#98D8C8",
    "Personal Care": "#F7DC6F",
    "Other":         "#AEB6BF",
}


def get_category_color(category: str) -> str:
    """Return the hex color for a given category."""
    return CATEGORY_COLORS.get(category, "#AEB6BF")


def get_all_colors() -> list:
    """Return the full list of category colors in order."""
    return list(CATEGORY_COLORS.values())
