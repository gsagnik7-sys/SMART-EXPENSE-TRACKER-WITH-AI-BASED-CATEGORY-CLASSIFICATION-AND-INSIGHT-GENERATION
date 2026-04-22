"""
classifier.py
-------------
AI-powered expense category classifier using Naive Bayes + TF-IDF.
Trains on a built-in dataset and saves/loads the model as a .pkl file.
"""

import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# ─── Training Dataset ────────────────────────────────────────────────────────
# Each entry is (product_description, category)
TRAINING_DATA = [
    # Food & Dining
    ("burger", "Food"), ("pizza", "Food"), ("coffee", "Food"),
    ("lunch", "Food"), ("dinner", "Food"), ("breakfast", "Food"),
    ("sandwich", "Food"), ("sushi", "Food"), ("biryani", "Food"),
    ("pasta", "Food"), ("noodles", "Food"), ("chai", "Food"),
    ("tea", "Food"), ("snacks", "Food"), ("groceries", "Food"),
    ("vegetables", "Food"), ("fruits", "Food"), ("milk", "Food"),
    ("bread", "Food"), ("eggs", "Food"), ("restaurant", "Food"),
    ("cafe", "Food"), ("bakery", "Food"), ("ice cream", "Food"),
    ("juice", "Food"), ("water bottle", "Food"), ("chicken", "Food"),
    ("swiggy", "Food"), ("zomato", "Food"), ("dominos", "Food"),

    # Travel & Transport
    ("uber", "Travel"), ("ola", "Travel"), ("cab", "Travel"),
    ("taxi", "Travel"), ("bus ticket", "Travel"), ("train ticket", "Travel"),
    ("flight", "Travel"), ("metro", "Travel"), ("auto", "Travel"),
    ("fuel", "Travel"), ("petrol", "Travel"), ("diesel", "Travel"),
    ("parking", "Travel"), ("toll", "Travel"), ("rapido", "Travel"),
    ("bike rental", "Travel"), ("car rental", "Travel"), ("airport", "Travel"),
    ("hotel", "Travel"), ("airbnb", "Travel"), ("hostel", "Travel"),

    # Shopping
    ("shirt", "Shopping"), ("jeans", "Shopping"), ("shoes", "Shopping"),
    ("dress", "Shopping"), ("jacket", "Shopping"), ("clothes", "Shopping"),
    ("amazon", "Shopping"), ("flipkart", "Shopping"), ("meesho", "Shopping"),
    ("bag", "Shopping"), ("watch", "Shopping"), ("sunglasses", "Shopping"),
    ("accessories", "Shopping"), ("earphones", "Shopping"), ("phone case", "Shopping"),
    ("furniture", "Shopping"), ("decor", "Shopping"), ("curtains", "Shopping"),

    # Entertainment
    ("netflix", "Entertainment"), ("spotify", "Entertainment"),
    ("movie ticket", "Entertainment"), ("concert", "Entertainment"),
    ("game", "Entertainment"), ("steam", "Entertainment"),
    ("youtube premium", "Entertainment"), ("disney plus", "Entertainment"),
    ("prime video", "Entertainment"), ("hotstar", "Entertainment"),
    ("bowling", "Entertainment"), ("arcade", "Entertainment"),

    # Health & Medical
    ("medicine", "Health"), ("pharmacy", "Health"), ("doctor", "Health"),
    ("hospital", "Health"), ("gym", "Health"), ("fitness", "Health"),
    ("yoga", "Health"), ("supplements", "Health"), ("vitamins", "Health"),
    ("dentist", "Health"), ("eye checkup", "Health"), ("lab test", "Health"),

    # Utilities & Bills
    ("electricity bill", "Utilities"), ("water bill", "Utilities"),
    ("internet", "Utilities"), ("wifi", "Utilities"), ("gas bill", "Utilities"),
    ("phone bill", "Utilities"), ("mobile recharge", "Utilities"),
    ("broadband", "Utilities"), ("dth", "Utilities"), ("cable tv", "Utilities"),

    # Education
    ("books", "Education"), ("course", "Education"), ("udemy", "Education"),
    ("coursera", "Education"), ("tuition", "Education"), ("stationery", "Education"),
    ("notebook", "Education"), ("pen", "Education"), ("school fees", "Education"),
    ("college fees", "Education"), ("library", "Education"),

    # Personal Care
    ("haircut", "Personal Care"), ("salon", "Personal Care"),
    ("shampoo", "Personal Care"), ("soap", "Personal Care"),
    ("face wash", "Personal Care"), ("moisturizer", "Personal Care"),
    ("perfume", "Personal Care"), ("makeup", "Personal Care"),
    ("nail polish", "Personal Care"), ("razor", "Personal Care"),
]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "classifier_model.pkl")


def _build_pipeline() -> Pipeline:
    """Create a sklearn Pipeline with TF-IDF + Naive Bayes."""
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),   # unigrams + bigrams
            lowercase=True,
            max_features=5000,
        )),
        ("clf", MultinomialNB(alpha=0.5)),
    ])


def train_and_save_model() -> Pipeline:
    """Train the classifier on TRAINING_DATA and save it to disk."""
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    texts, labels = zip(*TRAINING_DATA)
    model = _build_pipeline()
    model.fit(texts, labels)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"[Classifier] Model trained on {len(texts)} samples and saved.")
    return model


def load_model() -> Pipeline:
    """Load model from disk; train fresh if not found."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return train_and_save_model()


def predict_category(product_name: str) -> str:
    """
    Predict the expense category for a given product name.

    Args:
        product_name: e.g. "burger", "uber ride"

    Returns:
        Category string, e.g. "Food", "Travel"
    """
    if not product_name or not product_name.strip():
        return "Other"

    model = load_model()
    prediction = model.predict([product_name.strip().lower()])[0]
    return prediction


def get_prediction_confidence(product_name: str) -> dict:
    """Return category probabilities for a product name."""
    model = load_model()
    probs = model.predict_proba([product_name.strip().lower()])[0]
    classes = model.classes_
    return dict(sorted(zip(classes, probs), key=lambda x: -x[1]))


# ─── Quick self-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    train_and_save_model()
    tests = ["burger", "uber", "netflix", "gym", "electricity bill", "shirt"]
    for t in tests:
        print(f"  '{t}' → {predict_category(t)}")
