
import pandas as pd
import re

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

        self.model.fit(
            X_train,
            y_train
        )

        self.trained = True

        print("Training completed.")


    def predict(self, message):

        if not self.trained:
            self.train()

        text = str(message).lower()


        # =====================================================
        # PAYMENT SIGNALS
        # =====================================================

        payment_patterns = [
            r"\bpayment\b",
            r"\bamazon pay\b",
            r"\bcredit card\b",
            r"\bdebit card\b",
            r"\bgift card\b",
            r"\bbilling\b",
            r"\bbilled\b",
            r"\bcharged\b",
            r"\bcharge\b",
            r"\bcashback\b",
            r"\bcoupon\b",
            r"\bvoucher\b",
            r"\btransaction\b",
            r"\bpaid\b",
            r"\bpay\b"
        ]


        # =====================================================
        # PRIME SIGNALS
        # =====================================================

        prime_patterns = [
            r"\bprime\b",
            r"\bprime membership\b",
            r"\bprime member\b",
            r"\bprime subscription\b"
        ]


        # =====================================================
        # REFUND / RETURN SIGNALS
        # =====================================================

        refund_patterns = [
            r"\brefund\b",
            r"\brefunded\b",
            r"\breturn\b",
            r"\breturned\b",
            r"\bmoney back\b",
            r"\breimburse\b"
        ]


        # =====================================================
        # DELIVERY NOT RECEIVED
        # =====================================================

        not_received_patterns = [

            r"delivered but",
            r"marked delivered",
            r"says delivered",

            r"not received",
            r"didn't receive",
            r"did not receive",
            r"didnt receive",

            r"never received",
            r"never arrived",

            r"missing package",
            r"missing parcel",

            r"package.*missing",
            r"parcel.*missing"
        ]


        # =====================================================
        # DELIVERY SIGNALS
        # =====================================================

        delivery_patterns = [

            r"\bdelivery\b",
            r"\bdeliver\b",
            r"\bdelivered\b",
            r"\bdelivering\b",

            r"\bshipping\b",
            r"\bshipped\b",
            r"\bshipment\b",

            r"\btracking\b",
            r"\btracked\b",
            r"\btrack my\b",

            r"\bcourier\b",

            r"\bparcel\b",
            r"\bpackage\b",

            r"\bout for delivery\b",

            r"\barrive\b",
            r"\barrived\b",
            r"\barrival\b",
            r"\barriving\b",

            r"\bdelayed\b",
            r"\bdelay\b",

            r"\blate\b",

            r"\bnext.?day\b",
            r"\bone.?day shipping\b",

            r"\bguaranteed delivery\b",

            r"\bdelivery date\b",
            r"\bdelivery time\b",

            r"\bdelivery guy\b",
            r"\bdelivery boy\b",

            r"\bdeliver to my\b",
            r"\bdeliver to\b"
        ]


        # =====================================================
        # PRIORITY 1
        # DELIVERY NOT RECEIVED
        # =====================================================

        if any(
            re.search(pattern, text)
            for pattern in not_received_patterns
        ):
            return "delivery_not_received"


        # =====================================================
        # PRIORITY 2
        # PAYMENT
        # =====================================================

        if any(
            re.search(pattern, text)
            for pattern in payment_patterns
        ):
            return "payment_issue"


        # =====================================================
        # PRIORITY 3
        # PRIME
        # =====================================================

        if any(
            re.search(pattern, text)
            for pattern in prime_patterns
        ):
            return "prime_membership"


        # =====================================================
        # PRIORITY 4
        # REFUND / RETURN
        # =====================================================

        if any(
            re.search(pattern, text)
            for pattern in refund_patterns
        ):
            return "refund_return"


        # =====================================================
        # PRIORITY 5
        # DELIVERY
        # =====================================================

        if any(
            re.search(pattern, text)
            for pattern in delivery_patterns
        ):
            return "delivery_issue"


        # =====================================================
        # MACHINE LEARNING FALLBACK
        # =====================================================

        return self.model.predict([message])[0]


    def predict_batch(self, messages):

        if not self.trained:
            self.train()

        predictions = []

        for message in messages:

            predictions.append(
                self.predict(message)
            )

        return predictions


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    classifier = IntentClassifier()

    classifier.train()


    print("\n==============================")
    print("GOLDEN SET RESULTS")
    print("==============================")


    golden_df = pd.read_csv(
        GOLDEN_FILE
    )

    golden_df = golden_df.dropna(
        subset=["customer_message", "intent"]
    )


    X_test = golden_df["customer_message"]

    y_test = golden_df["intent"]


    predictions = classifier.predict_batch(
        X_test
    )


    accuracy = accuracy_score(
        y_test,
        predictions
    )


    print(
        f"\nAccuracy: {accuracy:.3f}"
    )


    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )


    # =========================================================
    # EXAMPLE PREDICTIONS
    # =========================================================

    examples = [

        "My package has not arrived yet",

        "I need a refund for my order",

        "My Amazon Pay payment failed",

        "I cannot login to my account",

        "I want to cancel my order",

        "How much does Amazon Prime cost?",

        "My delivery is two days late",

        "My order says out for delivery",

        "The courier has not delivered my package"
    ]


    print("\n==============================")
    print("EXAMPLE PREDICTIONS")
    print("==============================")


    for message in examples:

        prediction = classifier.predict(
            message
        )

        print(
            f"\nCustomer: {message}"
        )

        print(
            f"Predicted intent: {prediction}"
        )

