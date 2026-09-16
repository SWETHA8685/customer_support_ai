import pandas as pd
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


GOLDEN_FILE = "data/golden/golden_set.csv"
TRAINING_FILE = "data/processed/amazonhelp_training.csv"


def clean_text(text):
    if pd.isna(text):
        return ""

    text = str(text).lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"@\w+", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def train_intent_classifier():

    train_df = pd.read_csv(TRAINING_FILE)

    train_df = train_df.dropna(
        subset=["customer_message", "intent"]
    ).copy()

    train_df["clean_message"] = train_df["customer_message"].apply(
        clean_text
    )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=50000
    )

    X_train = vectorizer.fit_transform(
        train_df["clean_message"]
    )

    y_train = train_df["intent"]

    classifier = LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    )

    classifier.fit(X_train, y_train)

    return vectorizer, classifier


def predict_decision(message):

    text = clean_text(message)

    escalation_keywords = [
        "complaint",
        "complain",
        "refund",
        "charged",
        "charge",
        "cancel",
        "cancelled",
        "canceled",
        "not received",
        "never received",
        "missing",
        "not delivered",
        "late",
        "delayed",
        "still",
        "already contacted",
        "contacted support",
        "no response",
        "no answer",
        "nobody",
        "human",
        "representative",
        "call me",
        "speak to someone",
        "wrong",
        "damaged",
        "broken",
        "not working",
        "can't",
        "cannot",
        "unable"
    ]

    for keyword in escalation_keywords:
        if keyword in text:
            return "escalate"

    return "auto_handle"


def main():

    print("=" * 60)
    print("SIMPLE BASELINE")
    print("=" * 60)

    golden_df = pd.read_csv(GOLDEN_FILE)

    print(f"Golden examples: {len(golden_df)}")

    print("\nTraining TF-IDF + Logistic Regression...")

    vectorizer, classifier = train_intent_classifier()

    messages = golden_df["customer_message"].fillna("").apply(
        clean_text
    )

    X_test = vectorizer.transform(messages)

    predictions = classifier.predict(X_test)

    golden_df["predicted_intent"] = predictions

    golden_df["predicted_decision"] = golden_df[
        "customer_message"
    ].apply(predict_decision)

    # ---------------------------------------------------------
    # INTENT RESULTS
    # ---------------------------------------------------------

    intent_accuracy = accuracy_score(
        golden_df["intent"],
        golden_df["predicted_intent"]
    )

    print("\n" + "=" * 60)
    print("INTENT CLASSIFICATION RESULTS")
    print("=" * 60)

    print(f"\nIntent Accuracy: {intent_accuracy:.3f}")

    print("\nClassification Report:")

    print(
        classification_report(
            golden_df["intent"],
            golden_df["predicted_intent"],
            zero_division=0
        )
    )

    # ---------------------------------------------------------
    # DECISION RESULTS
    # ---------------------------------------------------------

    decision_accuracy = accuracy_score(
        golden_df["decision"],
        golden_df["predicted_decision"]
    )

    print("\n" + "=" * 60)
    print("AUTO-HANDLE / ESCALATE RESULTS")
    print("=" * 60)

    print(f"\nDecision Accuracy: {decision_accuracy:.3f}")

    labels = ["auto_handle", "escalate"]

    matrix = confusion_matrix(
        golden_df["decision"],
        golden_df["predicted_decision"],
        labels=labels
    )

    print("\nDecision Confusion Matrix:")
    print(matrix)

    # ---------------------------------------------------------
    # SAFETY METRICS
    # ---------------------------------------------------------

    expected_escalations = (
        golden_df["decision"] == "escalate"
    ).sum()

    correct_escalations = (
        (golden_df["decision"] == "escalate")
        &
        (golden_df["predicted_decision"] == "escalate")
    ).sum()

    unsafe_auto_handles = (
        (golden_df["decision"] == "escalate")
        &
        (golden_df["predicted_decision"] == "auto_handle")
    ).sum()

    unnecessary_escalations = (
        (golden_df["decision"] == "auto_handle")
        &
        (golden_df["predicted_decision"] == "escalate")
    ).sum()

    escalation_recall = (
        correct_escalations / expected_escalations
        if expected_escalations > 0
        else 0
    )

    print("\nDecision Safety Metrics:")
    print(f"Expected escalations: {expected_escalations}")
    print(f"Correct escalations: {correct_escalations}")
    print(f"Escalation recall: {escalation_recall:.3f}")
    print(f"Unsafe auto-handles: {unsafe_auto_handles}")
    print(f"Unnecessary escalations: {unnecessary_escalations}")

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    output_file = "evaluation/simple_baseline_results.csv"

    golden_df.to_csv(
        output_file,
        index=False
    )

    print("\nResults saved to:")
    print(output_file)

    print("\n" + "=" * 60)
    print("SIMPLE BASELINE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()