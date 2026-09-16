import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report


TRAIN_FILE = "data/processed/amazonhelp_training.csv"
GOLDEN_FILE = "data/golden/golden_set.csv"


class IntentClassifier:

    def __init__(self):
        self.model = Pipeline([
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

        self.trained = False

    def train(self):
        print("Loading training data...")

        train_df = pd.read_csv(TRAIN_FILE)
        train_df = train_df.dropna(
            subset=["customer_message", "intent"]
        )

        X_train = train_df["customer_message"]
        y_train = train_df["intent"]

        print("Training examples:", len(train_df))

        print("\nTraining classifier...")
        self.model.fit(X_train, y_train)

        self.trained = True

        print("Training completed.")

    def predict(self, message):
        if not self.trained:
            self.train()

        return self.model.predict([message])[0]

    def predict_batch(self, messages):
        if not self.trained:
            self.train()

        return self.model.predict(messages)


if __name__ == "__main__":

    classifier = IntentClassifier()

    classifier.train()

    print("\n==============================")
    print("GOLDEN SET RESULTS")
    print("==============================")

    golden_df = pd.read_csv(GOLDEN_FILE)
    golden_df = golden_df.dropna(
        subset=["customer_message", "intent"]
    )

    X_test = golden_df["customer_message"]
    y_test = golden_df["intent"]

    predictions = classifier.predict_batch(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print(f"\nAccuracy: {accuracy:.3f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    examples = [
        "My package has not arrived yet",
        "I need a refund for my order",
        "My Amazon Pay payment failed",
        "I cannot login to my account",
        "I want to cancel my order",
        "How much does Amazon Prime cost?"
    ]

    print("\n==============================")
    print("EXAMPLE PREDICTIONS")
    print("==============================")

    for message in examples:
        prediction = classifier.predict(message)

        print(f"\nCustomer: {message}")
        print(f"Predicted intent: {prediction}")