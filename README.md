<<<<<<< HEAD
# 💸 Smart Expense Tracker

A production-quality Python desktop application for tracking personal expenses with an **AI-powered auto-category classifier** and a beautiful dark-themed GUI.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Add Expenses** | Amount, product name, optional category |
| **AI Auto-Category** | Predicts category (Food, Travel, etc.) from product name using NLP |
| **View Expenses** | Sortable table with delete-row support |
| **Summary** | Per-category totals, counts, percentages |
| **Pie Chart** | Donut-style category spending chart |
| **Bar Chart** | Category comparison bar chart |
| **CSV Storage** | All data saved to `data/expenses.csv` |

---

## 🏗 Project Structure

```
expense_tracker/
├── main.py              # Entry point — trains model, launches GUI
├── gui.py               # Full Tkinter GUI (tabs, charts, forms)
├── expense_manager.py   # CRUD logic using pandas + CSV
├── classifier.py        # AI classifier (TF-IDF + Naive Bayes)
├── utils.py             # Shared helpers (formatting, colors)
├── data/
│   └── expenses.csv     # Auto-created on first run
├── models/
│   └── classifier_model.pkl  # Auto-saved after first training
├── requirements.txt
└── README.md
```

---

## 🚀 Setup & Run

### 1. Clone / Download the project

```bash
cd expense_tracker
```

### 2. (Recommended) Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python main.py
```

> `tkinter` is included with Python by default. If you're on Linux and it's missing:
> ```bash
> sudo apt install python3-tk
> ```

---

## 🤖 How the AI Works

The classifier uses **scikit-learn**:

1. **TF-IDF Vectorizer** converts product text into numerical features (with bigrams)
2. **Multinomial Naive Bayes** classifies into one of 9 categories
3. Trained on ~160 labelled examples inside `classifier.py`
4. Model is saved as `models/classifier_model.pkl` after first run

**Supported categories:**
Food · Travel · Shopping · Entertainment · Health · Utilities · Education · Personal Care · Other

---

## 📋 Example Usage

| Product Name | AI Predicted Category |
|---|---|
| burger | Food |
| uber ride | Travel |
| netflix | Entertainment |
| electricity bill | Utilities |
| gym fee | Health |
| shirt | Shopping |
| udemy course | Education |

---

## 🛠 Tech Stack

- **Python 3.8+**
- **tkinter** — GUI
- **pandas** — Data storage & manipulation
- **scikit-learn** — NLP classifier
- **matplotlib** — Charts & visualizations
- **numpy** — Numerical operations

---

## 📄 License

MIT — free to use, modify, and distribute.
=======
# SMART-EXPENSE-TRACKER-WITH-AI-BASED-CATEGORY-CLASSIFICATION-AND-INSIGHT-GENERATION
Smart expense tracker with AI-based category prediction using NLP (TF-IDF + Naive Bayes). Includes interactive GUI, data visualization, insights generation, and CSV-based storage for efficient financial management.
>>>>>>> d5baafa2a4589a4fd2421af21b77c6384a14fb32
