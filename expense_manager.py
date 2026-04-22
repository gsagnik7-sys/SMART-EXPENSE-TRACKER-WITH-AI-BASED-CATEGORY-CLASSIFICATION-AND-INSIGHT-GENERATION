"""
expense_manager.py
------------------
Handles all expense data operations:
  - Adding expenses
  - Loading/saving to CSV
  - Computing summaries
Uses pandas for data manipulation.
"""

import os
from datetime import datetime
import pandas as pd

# ─── Config ──────────────────────────────────────────────────────────────────
DATA_DIR  = os.path.join(os.path.dirname(__file__), "data")
CSV_PATH  = os.path.join(DATA_DIR, "expenses.csv")

COLUMNS = ["id", "date", "product", "amount", "category"]

VALID_CATEGORIES = [
    "Food", "Travel", "Shopping", "Entertainment",
    "Health", "Utilities", "Education", "Personal Care", "Other"
]


# ─── Helpers ─────────────────────────────────────────────────────────────────
def _ensure_csv_exists():
    """Create the data directory and empty CSV if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_PATH, index=False)


def _load_df() -> pd.DataFrame:
    """Load expenses from CSV into a DataFrame."""
    _ensure_csv_exists()
    try:
        df = pd.read_csv(CSV_PATH)
        if df.empty or list(df.columns) != COLUMNS:
            return pd.DataFrame(columns=COLUMNS)
        return df
    except Exception:
        return pd.DataFrame(columns=COLUMNS)


def _save_df(df: pd.DataFrame):
    """Save DataFrame back to CSV."""
    _ensure_csv_exists()
    df.to_csv(CSV_PATH, index=False)


def _next_id(df: pd.DataFrame) -> int:
    """Generate the next auto-increment ID."""
    if df.empty:
        return 1
    return int(df["id"].max()) + 1


# ─── Public API ──────────────────────────────────────────────────────────────
def add_expense(product: str, amount: float, category: str) -> dict:
    """
    Add a new expense record.

    Args:
        product:  Product/service name (e.g. "Burger", "Uber")
        amount:   Cost as a float (e.g. 150.00)
        category: Category string (e.g. "Food")

    Returns:
        The newly added expense as a dict.

    Raises:
        ValueError: If inputs are invalid.
    """
    # ── Validate ──
    product = product.strip()
    if not product:
        raise ValueError("Product name cannot be empty.")

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise ValueError("Amount must be a valid number.")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    category = category.strip().title() if category else "Other"
    if category not in VALID_CATEGORIES:
        category = "Other"

    # ── Build record ──
    df = _load_df()
    new_row = {
        "id":       _next_id(df),
        "date":     datetime.now().strftime("%Y-%m-%d %H:%M"),
        "product":  product.title(),
        "amount":   round(amount, 2),
        "category": category,
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    _save_df(df)
    return new_row


def get_all_expenses() -> pd.DataFrame:
    """Return all expenses as a DataFrame (newest first)."""
    df = _load_df()
    if df.empty:
        return df
    return df.sort_values("id", ascending=False).reset_index(drop=True)


def get_total_spending() -> float:
    """Return the sum of all expense amounts."""
    df = _load_df()
    if df.empty:
        return 0.0
    return round(float(df["amount"].sum()), 2)


def get_category_summary() -> pd.DataFrame:
    """
    Return per-category totals sorted descending.

    Returns:
        DataFrame with columns: category, total, count, percentage
    """
    df = _load_df()
    if df.empty:
        return pd.DataFrame(columns=["category", "total", "count", "percentage"])

    summary = (
        df.groupby("category")["amount"]
        .agg(total="sum", count="count")
        .reset_index()
        .sort_values("total", ascending=False)
    )
    grand_total = summary["total"].sum()
    summary["percentage"] = (summary["total"] / grand_total * 100).round(1)
    summary["total"] = summary["total"].round(2)
    return summary.reset_index(drop=True)


def delete_expense(expense_id: int) -> bool:
    """
    Delete an expense by its ID.

    Returns:
        True if deleted, False if not found.
    """
    df = _load_df()
    before = len(df)
    df = df[df["id"] != expense_id]
    if len(df) == before:
        return False
    _save_df(df)
    return True


def clear_all_expenses():
    """Wipe all expense records (keeps the CSV with headers)."""
    df = pd.DataFrame(columns=COLUMNS)
    _save_df(df)


# ─── Quick test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    clear_all_expenses()
    add_expense("Burger",       150,  "Food")
    add_expense("Uber Ride",    220,  "Travel")
    add_expense("Netflix",      499,  "Entertainment")
    add_expense("Gym Fee",      800,  "Health")
    add_expense("Electricity",  1200, "Utilities")

    print(get_all_expenses().to_string())
    print("\nTotal: ₹", get_total_spending())
    print("\nCategory Summary:")
    print(get_category_summary().to_string())
