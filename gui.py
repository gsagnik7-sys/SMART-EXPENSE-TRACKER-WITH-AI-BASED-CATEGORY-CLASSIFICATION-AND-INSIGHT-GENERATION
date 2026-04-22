"""
gui.py
------
Full Tkinter GUI for the Smart Expense Tracker.
Provides tabs for:
  - Add Expense  (with AI auto-category)
  - View Expenses
  - Summary
  - Graphs
"""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime

from expense_manager import (
    add_expense, get_all_expenses, get_total_spending,
    get_category_summary, clear_all_expenses, VALID_CATEGORIES
)
from classifier import predict_category
from utils import format_currency, validate_amount, get_category_color, get_all_colors


# ─── Color Theme ─────────────────────────────────────────────────────────────
BG_DARK      = "#1A1A2E"
BG_MID       = "#16213E"
BG_CARD      = "#0F3460"
ACCENT       = "#00E5FF"
ACCENT_LIGHT = "#4FC3F7"
TEXT_MAIN    = "#EAEAEA"
TEXT_MUTED   = "#A0A0B0"
SUCCESS      = "#4CAF50"
WARNING      = "#FF9800"
FONT_TITLE   = ("Segoe UI", 22, "bold")
FONT_HEADER  = ("Segoe UI", 13, "bold")
FONT_BODY    = ("Segoe UI", 11)
FONT_SMALL   = ("Segoe UI", 9)
FONT_MONO    = ("Consolas", 10)


class ExpenseTrackerApp:
    """Main application window with tabbed interface."""

    def __init__(self, root):
        self.root = root
        self._configure_root()
        self._apply_theme()
        self._build_header()
        self._build_tabs()
        self._build_status_bar()

    
    def _export_data(self):
        try:
            df = get_all_expenses()

            if df.empty:
                messagebox.showinfo("No Data", "No expenses to export.")
                return

            file_name = f"expenses_{datetime.now().strftime('%Y-%m-%d')}.csv"
            df.to_csv(file_name, index=False)

            messagebox.showinfo("Success", f"Data exported as {file_name}")

        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    
    
    # ── Setup ─────────────────────────────────────────────────────────────────
    def _configure_root(self):
        self.root.title("💸 Smart Expense Tracker")
        self.root.geometry("950x700")
        self.root.minsize(800, 600)
        self.root.configure(bg=BG_DARK)
        # Center on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - 950) // 2
        y = (self.root.winfo_screenheight() - 700) // 2
        self.root.geometry(f"950x700+{x}+{y}")

    def _apply_theme(self):
        """Style the ttk Notebook and Treeview widgets."""
        style = ttk.Style()

        # Notebook (tab bar)
        style.configure("Custom.TNotebook",
                         background=BG_DARK, borderwidth=0)
        style.configure("Custom.TNotebook.Tab",
                         background=BG_MID, foreground=TEXT_MUTED,
                         padding=(16, 8), font=FONT_BODY)
        style.map("Custom.TNotebook.Tab",
                  background=[("selected", BG_CARD)],
                  foreground=[("selected", ACCENT_LIGHT)])

        # Treeview
        style.configure("Custom.Treeview",
                         background=BG_MID, foreground=TEXT_MAIN,
                         fieldbackground=BG_MID, rowheight=28,
                         font=FONT_BODY, borderwidth=0)
        style.configure("Custom.Treeview.Heading",
                         background=BG_CARD, foreground=ACCENT_LIGHT,
                         font=FONT_HEADER, relief="flat")
        style.map("Custom.Treeview",
                  background=[("selected", ACCENT)])

        # Scrollbar
        style.configure("Custom.Vertical.TScrollbar",
                         background=BG_CARD, troughcolor=BG_MID,
                         arrowcolor=TEXT_MUTED)

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self):
        header = tk.Frame(self.root, bg="#0B1D3A", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header,
    text="💸 Smart Expense Tracker",
    font=("Segoe UI", 20, "bold"),
    fg="#00E5FF",
    bg="#0B1D3A"
)

        self.total_label = tk.Label(
            header, text="Total: ₹0.00",
            font=FONT_HEADER, fg=SUCCESS, bg=BG_CARD
        )
        self.total_label.pack(side="right", padx=20)
        self._refresh_total()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    def _build_tabs(self):
        self.notebook = ttk.Notebook(self.root, style="Custom.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(5, 0))

        self._tab_add      = tk.Frame(self.notebook, bg=BG_DARK)
        self._tab_view     = tk.Frame(self.notebook, bg=BG_DARK)
        self._tab_summary  = tk.Frame(self.notebook, bg=BG_DARK)
        self._tab_graphs   = tk.Frame(self.notebook, bg=BG_DARK)

        self.notebook.add(self._tab_add,     text="  ➕  Add Expense  ")
        self.notebook.add(self._tab_view,    text="  📋  View Expenses  ")
        self.notebook.add(self._tab_summary, text="  📊  Summary  ")
        self.notebook.add(self._tab_graphs,  text="  📈  Graphs  ")

        self._build_add_tab()
        self._build_view_tab()
        self._build_summary_tab()
        self._build_graphs_tab()

        # Refresh data when switching to View/Summary tabs
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

    # ── Add Expense Tab ───────────────────────────────────────────────────────
    def _build_add_tab(self):
        frame = self._tab_add

        # Card container
        card = tk.Frame(frame, bg=BG_CARD, padx=35, pady=30,
                relief="raised", bd=2)
        card.place(relx=0.5, rely=0.5, anchor="center", width=520)

        tk.Label(card, text="Add New Expense", font=FONT_HEADER,
                 fg=ACCENT_LIGHT, bg=BG_CARD).grid(
            row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        # ── Product Name ──
        self._lbl(card, "Product / Service Name", 1)
        self.entry_product = self._entry(card, 1, "e.g. Burger, Uber Ride, Netflix…")
        # Trigger AI on focus-out
        self.entry_product.bind("<FocusOut>", self._ai_autofill)

        # ── Amount ──
        self._lbl(card, "Amount (₹)", 2)
        self.entry_amount = self._entry(card, 2, "e.g. 250")

        # ── Category ──
        self._lbl(card, "Category  (leave blank for AI auto-detect)", 5)
        self.category_var = tk.StringVar(value="")
        cat_combo = ttk.Combobox(
            card, textvariable=self.category_var,
            values=[""] + VALID_CATEGORIES,
            state="readonly", width=35, font=FONT_BODY
        )
        cat_combo.grid(row=6, column=1, sticky="ew", pady=8)

        # ── AI Tag ──
        self.ai_tag = tk.Label(card, text="", font=FONT_SMALL,
                               fg=SUCCESS, bg=BG_CARD)
        self.ai_tag.grid(row=7, column=1, sticky="w", pady=(5, 10))

        # ── Buttons ──
        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=(10, 0))

        self._btn(btn_frame, "➕  Add Expense", self._handle_add,
                  ACCENT, "white", side="left", padx=6)
        self._btn(btn_frame, "🗑  Clear All", self._handle_clear_all,
                  "#444", TEXT_MUTED, side="left", padx=6)

        card.columnconfigure(1, weight=1)

    def _lbl(self, parent, text, row):
        tk.Label(parent, text=text, font=FONT_BODY,
                 fg=TEXT_MUTED, bg=BG_CARD
                 ).grid(row=row * 2 - 1, column=0, columnspan=2,
                        sticky="w", pady=(10, 2))

    def _entry(self, parent, row, placeholder=""):
        var = tk.StringVar()
        e = tk.Entry(parent, textvariable=var, font=FONT_BODY,
                     bg=BG_MID, fg=TEXT_MAIN, insertbackground=TEXT_MAIN,
                     relief="flat", bd=0, width=38,
                     highlightthickness=2, highlightcolor=ACCENT,
                     highlightbackground="#333")
        e.grid(row=row * 2, column=1, sticky="ew", pady=4, ipady=6, padx=(4, 0))
        # Placeholder
        e.insert(0, placeholder)
        e.config(fg=TEXT_MUTED)
        e.bind("<FocusIn>",  lambda ev, w=e, p=placeholder: self._clear_ph(ev, w, p))
        e.bind("<FocusOut>", lambda ev, w=e, p=placeholder: self._restore_ph(ev, w, p))
        return e

    @staticmethod
    def _clear_ph(event, widget, placeholder):
        if widget.get() == placeholder:
            widget.delete(0, "end")
            widget.config(fg=TEXT_MAIN)

    @staticmethod
    def _restore_ph(event, widget, placeholder):
        if not widget.get():
            widget.insert(0, placeholder)
            widget.config(fg=TEXT_MUTED)

    def _btn(self, parent, text, cmd, bg, fg, side="left", padx=4):
        tk.Button(parent,
        text=text,
        command=cmd,
        bg=bg,
        fg=fg,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        bd=0,
        padx=16,
        pady=10,
        activebackground=ACCENT_LIGHT,
        activeforeground="white",
        cursor="hand2"
    ).pack(side=side, padx=padx, pady=5)

    def _ai_autofill(self, event=None):
        """Predict category from product name and pre-fill if blank."""
        product = self.entry_product.get().strip()
        placeholder = "e.g. Burger, Uber Ride, Netflix…"
        if not product or product == placeholder:
            self.ai_tag.config(text="")
            return

        category = predict_category(product)
        self.ai_tag.config(text=f"🤖 AI suggests: {category}", fg=SUCCESS)

        # Only auto-fill if user hasn't chosen a category yet
        if not self.category_var.get():
            self.category_var.set(category)

    # ── Handle Add ────────────────────────────────────────────────────────────
    def _handle_add(self):
        product_raw = self.entry_product.get().strip()
        placeholder = "e.g. Burger, Uber Ride, Netflix…"

        if not product_raw or product_raw == placeholder:
            messagebox.showwarning("Missing Info", "Please enter a product name.")
            return

        amount_raw = self.entry_amount.get().strip()
        if amount_raw == "e.g. 250":
            amount_raw = ""

        amount = validate_amount(amount_raw)
        if amount is None:
            messagebox.showerror("Invalid Amount",
                                 "Please enter a valid positive number for amount.")
            return

        # Get category — AI if blank
        category = self.category_var.get().strip()
        if not category:
            category = predict_category(product_raw)

        try:
            record = add_expense(product_raw, amount, category)
            self._show_status(
                f"✅  Added: {record['product']}  |  {format_currency(record['amount'])}  |  {record['category']}"
            )
            self._refresh_total()
            self._reset_add_form()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _reset_add_form(self):
        for entry, ph in [
            (self.entry_product, "e.g. Burger, Uber Ride, Netflix…"),
            (self.entry_amount,  "e.g. 250"),
        ]:
            entry.delete(0, "end")
            entry.insert(0, ph)
            entry.config(fg=TEXT_MUTED)
        self.category_var.set("")
        self.ai_tag.config(text="")

    def _handle_clear_all(self):
        if messagebox.askyesno("Confirm", "Delete ALL expenses? This cannot be undone."):
            clear_all_expenses()
            self._refresh_total()
            self._show_status("🗑  All expenses cleared.")

    # ── View Expenses Tab ─────────────────────────────────────────────────────
    def _build_view_tab(self):
        frame = self._tab_view

        cols = ("ID", "Date", "Product", "Amount", "Category")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings",
                                  style="Custom.Treeview", selectmode="browse")

        widths = {"ID": 45, "Date": 130, "Product": 220, "Amount": 110, "Category": 140}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths[col], anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical",
                             command=self.tree.yview,
                             style="Custom.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set)

# Buttons FIRST
        btn_row = tk.Frame(frame, bg=BG_DARK)
        btn_row.pack(fill="x", padx=10, pady=(10, 5))

        self._btn(btn_row, "🗑  Delete Selected Row", self._delete_selected,
          "#444", WARNING, side="left")

        self._btn(btn_row, "📥 Export Data", self._export_data,
          ACCENT, "white", side="left", padx=6)

# THEN table
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        vsb.pack(side="right", fill="y", pady=10, padx=(0, 10))

    def _load_view(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        df = get_all_expenses()
        if df.empty:
            self.tree.insert("", "end", values=("—", "No expenses yet", "—", "—", "—"))
            return

        for _, row in df.iterrows():
            self.tree.insert("", "end",
                             values=(
                                 int(row["id"]),
                                 row["date"],
                                 row["product"],
                                 format_currency(row["amount"]),
                                 row["category"],
                             ))

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Row", "Please select a row to delete.")
            return
        item = self.tree.item(selected[0])
        expense_id = item["values"][0]
        if expense_id == "—":
            return
        if messagebox.askyesno("Confirm", f"Delete expense #{expense_id}?"):
            from expense_manager import delete_expense
            delete_expense(int(expense_id))
            self._load_view()
            self._refresh_total()
            self._show_status(f"🗑  Deleted expense #{expense_id}")

    # ── Summary Tab ───────────────────────────────────────────────────────────
    def _build_summary_tab(self):
        frame = self._tab_summary

        # Total banner
        self.summary_total_lbl = tk.Label(
            frame, text="", font=("Segoe UI", 16, "bold"),
            fg=SUCCESS, bg=BG_DARK
        )
        self.summary_total_lbl.pack(pady=(20, 5))
         
        self.insight_label = tk.Label(
           frame,
           text="",
           font=("Segoe UI", 11, "italic"),
           fg=ACCENT_LIGHT,
           bg=BG_DARK,
           wraplength=600,
           justify="center"
        )
        self.insight_label.pack(pady=(5, 15))     

        cols = ("Category", "Total Spent", "Transactions", "% of Total")
        self.summary_tree = ttk.Treeview(
            frame, columns=cols, show="headings",
            style="Custom.Treeview", selectmode="none"
        )
        widths = {"Category": 180, "Total Spent": 160, "Transactions": 130, "% of Total": 130}
        for col in cols:
            self.summary_tree.heading(col, text=col)
            self.summary_tree.column(col, width=widths[col], anchor="center")

        vsb2 = ttk.Scrollbar(frame, orient="vertical",
                              command=self.summary_tree.yview,
                              style="Custom.Vertical.TScrollbar")
        self.summary_tree.configure(yscrollcommand=vsb2.set)
        self.summary_tree.pack(side="left", fill="both", expand=True,
                                padx=(10, 0), pady=10)
        vsb2.pack(side="right", fill="y", pady=10, padx=(0, 10))

    def _load_summary(self):
        for row in self.summary_tree.get_children():
            self.summary_tree.delete(row)

        total = get_total_spending()
        self.summary_total_lbl.config(
            text=f"Total Spending:  {format_currency(total)}"
        )
        insight_text = self._generate_insights()
        self.insight_label.config(text=insight_text)

        df = get_category_summary()
        if df.empty:
            self.summary_tree.insert("", "end",
                                      values=("No data", "—", "—", "—"))
            return

        for _, row in df.iterrows():
            self.summary_tree.insert(
                "", "end",
                values=(
                    row["category"],
                    format_currency(row["total"]),
                    int(row["count"]),
                    f'{row["percentage"]}%',
                )
            )

    # ── Graphs Tab ────────────────────────────────────────────────────────────
    def _build_graphs_tab(self):
        frame = self._tab_graphs

        btn_row = tk.Frame(frame, bg=BG_DARK)
        btn_row.pack(fill="x", padx=14, pady=10)
        self._btn(btn_row, "🥧  Pie Chart",  self._show_pie,  ACCENT, "white", side="left", padx=6)
        self._btn(btn_row, "📊  Bar Chart",  self._show_bar,  BG_CARD, ACCENT_LIGHT, side="left", padx=6)
        self._btn(btn_row, "🔄  Refresh",    self._clear_graph, "#333", TEXT_MUTED, side="right", padx=6)

        self.graph_frame = tk.Frame(frame, bg=BG_DARK)
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _clear_graph(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

    def _get_chart_data(self):
        df = get_category_summary()
        if df.empty:
            messagebox.showinfo("No Data", "Add some expenses first!")
            return None, None
        return df["category"].tolist(), df["total"].tolist()

    def _show_pie(self):
        labels, values = self._get_chart_data()
        if labels is None:
            return
        self._clear_graph()

        colors = [get_category_color(l) for l in labels]
        fig, ax = plt.subplots(figsize=(7, 4.5), facecolor=BG_DARK)
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, colors=colors,
            autopct="%1.1f%%", startangle=140,
            pctdistance=0.82, wedgeprops=dict(width=0.6, edgecolor=BG_DARK, linewidth=2)
        )
        for t in texts:
            t.set_color(TEXT_MAIN)
            t.set_fontsize(9)
        for at in autotexts:
            at.set_color("#111")
            at.set_fontsize(8)
            at.set_fontweight("bold")
        ax.set_title("Spending by Category", color=ACCENT_LIGHT,
                     fontsize=13, fontweight="bold", pad=12)
        fig.tight_layout()
        self._embed_chart(fig)

    def _show_bar(self):
        labels, values = self._get_chart_data()
        if labels is None:
            return
        self._clear_graph()

        colors = [get_category_color(l) for l in labels]
        fig, ax = plt.subplots(figsize=(7, 4.5), facecolor=BG_DARK)
        ax.set_facecolor(BG_MID)
        bars = ax.bar(labels, values, color=colors,
                      edgecolor=BG_DARK, linewidth=1.5, width=0.6)

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(values) * 0.01,
                    f"₹{val:,.0f}", ha="center", va="bottom",
                    color=TEXT_MAIN, fontsize=8, fontweight="bold")

        ax.set_title("Category-wise Expense Comparison",
                     color=ACCENT_LIGHT, fontsize=13, fontweight="bold", pad=10)
        ax.set_ylabel("Amount (₹)", color=TEXT_MUTED, fontsize=10)
        ax.tick_params(axis="x", colors=TEXT_MAIN, labelsize=8, rotation=20)
        ax.tick_params(axis="y", colors=TEXT_MUTED)
        ax.spines[:].set_color("#333")
        ax.set_axisbelow(True)
        ax.yaxis.grid(True, color="#333", linewidth=0.6)
        fig.tight_layout()
        self._embed_chart(fig)

    def _embed_chart(self, fig):
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    # ── Status Bar ────────────────────────────────────────────────────────────
    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="Ready  •  Add an expense to get started.")
        bar = tk.Label(self.root, textvariable=self.status_var,
                       font=FONT_SMALL, fg=TEXT_MUTED, bg="#0D0D1A",
                       anchor="w", padx=12, pady=5)
        bar.pack(fill="x", side="bottom")

    def _show_status(self, msg: str):
        self.status_var.set(msg)
        self.root.after(6000, lambda: self.status_var.set("Ready"))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _refresh_total(self):
        total = get_total_spending()
        self.total_label.config(text=f"Total: {format_currency(total)}")
    def _generate_insights(self):
        df = get_category_summary()

        if df.empty:
         return "No data available."

    # Get highest spending category
        top_category = df.iloc[0]["category"]
        top_amount = df.iloc[0]["total"]
        percentage = df.iloc[0]["percentage"]

    # Insight logic
        if percentage > 40:
           return f"⚠️ You are spending {percentage}% on {top_category}. Try to reduce it."
        elif percentage > 25:
           return f"💡 Significant spending on {top_category} ({percentage}%). Keep an eye on it."
        else:
           return f"✅ Your spending is balanced. Top category: {top_category} ({percentage}%)."    

    def _on_tab_change(self, event):
        tab = self.notebook.index("current")
        if tab == 1:
            self._load_view()
        elif tab == 2:
            self._load_summary()
