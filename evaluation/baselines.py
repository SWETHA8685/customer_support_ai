import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report


GOLDEN_FILE = "data/golden/golden_set.csv"
TRAIN_FILE = "data/processed/amazonhelp_training.csv"


def load_data():
    golden = pd.read_csv(GOLDEN_FILE)
    golden = golden.dropna(
        subset=["customer_message", "intent"]
    )

    train = pd.read_csv(TRAIN_FILE)
    train = train.dropna(
        subset=["customer_message", "intent"]
    )

    return train, golden


def majority_baseline(golden):
    """
    Trivial baseline:
    always predict the most common intent.
    """

    majority_intent = golden["intent"].value_counts().idxmax()

    predictions = [
        majority_intent
        for _ in range(len(golden))
    ]

    accuracy = accuracy_score(
        golden["intent"],
        predictions
    )

    print("\n")
    print("=" * 60)
    print("BASELINE 1: MAJORITY CLASS")
    print("=" * 60)

    print(f"\nMajority intent: {majority_intent}")
    print(f"Accuracy: {accuracy:.3f}")

    print("\nClassification Report:")
    print(
        classification_report(
            golden["intent"],
            predictions,
            zero_division=0
        )
    )

    return accuracy


def tfidf_baseline(train, golden):
    """
    Simple baseline:
    TF-IDF + Logistic Regression.

    This is a standard text-classification baseline.
    """

    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                stop_words="english",
                ngram_range=(1, 2),
                max_features=20000
            )
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced"
            )
        )
    ])

    print("\n")
    print("=" * 60)
    print("BASELINE 2: TF-IDF + LOGISTIC REGRESSION")
    print("=" * 60)

    print("\nTraining baseline...")

    model.fit(
        train["customer_message"],
        train["intent"]
    )

    predictions = model.predict(
        golden["customer_message"]
    )

    accuracy = accuracy_score(
        golden["intent"],
        predictions
    )

    print("Training completed.")

    print(f"\nAccuracy: {accuracy:.3f}")

    print("\nClassification Report:")
    print(
        classification_report(
            golden["intent"],
            predictions,
            zero_division=0
        )
    )

    return accuracy


def main():

    print("Loading data...")

    train, golden = load_data()

    print(f"Training examples: {len(train)}")
    print(f"Golden examples: {len(golden)}")

    # ---------------------------------------------
    # BASELINE 1
    # ---------------------------------------------

    majority_accuracy = majority_baseline(
        golden
    )

    # ---------------------------------------------
    # BASELINE 2
    # ---------------------------------------------

    tfidf_accuracy = tfidf_baseline(
        train,
        golden
    )

    # ---------------------------------------------
    # SUMMARY
    # ---------------------------------------------

    print("\n")
    print("=" * 60)
    print("BASELINE SUMMARY")
    print("=" * 60)

    print(
        f"\nMajority baseline: "
        f"{majority_accuracy:.3f}"
    )

    print(
        f"TF-IDF + Logistic Regression: "
        f"{tfidf_accuracy:.3f}"
    )

    print(
        "\nOur current agent intent accuracy: "
        "0.960"
    )

    print("\nComparison:")
    print(
        f"Majority → Agent improvement: "
        f"{0.960 - majority_accuracy:+.3f}"
    )

    print(
        f"TF-IDF → Agent improvement: "
        f"{0.960 - tfidf_accuracy:+.3f}"
    )


if __name__ == "__main__":
    main()