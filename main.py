"""
main.py
-------
Entry point for the Smart Expense Tracker.
Trains the AI model on first run, then launches the GUI.
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import sys
import os

# Make sure local imports work regardless of working directory
sys.path.insert(0, os.path.dirname(__file__))


def main():
    # ── 1. Pre-train the AI classifier (fast, ~0.1s) ──────────────────────
    print("🤖  Initializing AI classifier…")
    from classifier import load_model
    load_model()          # trains & saves if model doesn't exist yet
    print("✅  AI classifier ready.")

    # ── 2. Ensure data directory exists ───────────────────────────────────
    from expense_manager import _ensure_csv_exists
    _ensure_csv_exists()

    # ── 3. Launch GUI ─────────────────────────────────────────────────────
    print("🖥   Launching GUI…")
    root = ttk.Window(themename="darkly")

    from gui import ExpenseTrackerApp
    app = ExpenseTrackerApp(root)

    root.mainloop()
    print("👋  Goodbye!")


if __name__ == "__main__":
    main()
