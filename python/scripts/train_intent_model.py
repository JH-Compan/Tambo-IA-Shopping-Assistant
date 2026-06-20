from __future__ import annotations

import json
from pathlib import Path
import sys
import unicodedata

from joblib import dump
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "intents.json"
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "intent_classifier.joblib"


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""

    collapsed = " ".join(text.strip().lower().split())
    return "".join(
        char for char in unicodedata.normalize("NFD", collapsed)
        if unicodedata.category(char) != "Mn"
    )


def load_dataset() -> tuple[list[str], list[str]]:
    with DATA_PATH.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    texts: list[str] = []
    labels: list[str] = []

    for intent, phrases in payload.items():
        for phrase in phrases:
            texts.append(normalize_text(phrase))
            labels.append(intent)

    return texts, labels


def build_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            (
                "vectorizer",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    min_df=1,
                    lowercase=True
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1000,
                    random_state=42
                ),
            ),
        ]
    )


def main() -> int:
    texts, labels = load_dataset()

    x_train, x_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.25,
        random_state=42,
        stratify=labels
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions, digits=4)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    dump(pipeline, MODEL_PATH)

    print(f"Model path: {MODEL_PATH}")
    print(f"Accuracy: {accuracy:.4f}")
    print("Classification report:")
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
