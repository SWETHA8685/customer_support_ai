import pandas as pd
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report


# ============================================================
# FILE PATHS
# ============================================================

TRAIN_FILE = "data/processed/amazonhelp_training.csv"
GOLDEN_FILE = "data/golden/golden_set.csv"


# ============================================================
# INTENT CLASSIFIER
# ============================================================

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


    # ========================================================
    # TRAIN MODEL
    # ========================================================

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


    # ========================================================
    # PREDICT SINGLE MESSAGE
    # ========================================================

    def predict(self, message):

        if not self.trained:
            self.train()

        text = str(message).lower()


        # ====================================================
        # 1. DELIVERY NOT RECEIVED
        # ====================================================
        # Most specific delivery problem.
        #
        # Examples:
        # "marked delivered but I never received it"
        # "package says delivered but no package"
        # ====================================================

        not_received_patterns = [

            r"\bdelivered but\b",
            r"\bmarked delivered\b",
            r"\bsays delivered\b",

            r"\bno package\b",
            r"\bno parcel\b",

            r"\bnot received\b",
            r"\bdidn't receive\b",
            r"\bdid not receive\b",
            r"\bdidnt receive\b",

            r"\bnever received\b",
            r"\bnever arrived\b",

            r"\bmissing package\b",
            r"\bmissing parcel\b",

            r"\bpackage.*missing\b",
            r"\bparcel.*missing\b",

            r"\bpackage.*never\b",
            r"\bparcel.*never\b",

            r"\bpackage.*not received\b",
            r"\bparcel.*not received\b"
        ]

        if any(
            re.search(pattern, text)
            for pattern in not_received_patterns
        ):
            return "delivery_not_received"


        # ====================================================
        # 2. DELIVERY-SPECIFIC PATTERNS
        # ====================================================
        # These must run BEFORE Prime and payment.
        #
        # Important:
        #
        # "Prime delivery promise"
        #
        # is a delivery issue, not a Prime membership issue.
        # ====================================================

        delivery_priority_patterns = [

            r"\bprime\b.*\bdelivery\b",
            r"\bdelivery\b.*\bprime\b",

            r"\bprime\b.*\bshipping\b",
            r"\bshipping\b.*\bprime\b",

            r"\bprime\b.*\bpackage\b",
            r"\bpackage\b.*\bprime\b",

            r"\bprime\b.*\bparcel\b",
            r"\bparcel\b.*\bprime\b",

            r"\bprime\b.*\barriv",
            r"\bprime\b.*\blate\b",

            r"\bprime\b.*\bout for delivery\b",

            r"\bprime\b.*\bdelivery promise\b",
            r"\bprime\b.*\bguaranteed delivery\b",

            r"\bone day delivery\b",
            r"\bone-day delivery\b",

            r"\bnext day delivery\b",
            r"\bnext-day delivery\b",

            r"\bdelivery promise\b",
            r"\bguaranteed delivery\b",

            r"\bout for delivery\b"
        ]

        if any(
            re.search(pattern, text)
            for pattern in delivery_priority_patterns
        ):
            return "delivery_issue"


        # ====================================================
        # 3. GENERAL DELIVERY PATTERNS
        # ====================================================

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

            r"\barrive\b",
            r"\barrived\b",
            r"\barrival\b",
            r"\barriving\b",

            r"\bdelayed\b",
            r"\bdelay\b",
            r"\blate\b",

            r"\bnext.?day\b",
            r"\bone.?day shipping\b",

            r"\bdelivery date\b",
            r"\bdelivery time\b",

            r"\bdelivery guy\b",
            r"\bdelivery boy\b",

            r"\bdeliver to my\b",
            r"\bdeliver to\b"
        ]

        if any(
            re.search(pattern, text)
            for pattern in delivery_patterns
        ):
            return "delivery_issue"


        # ====================================================
        # 4. PRODUCT-SPECIFIC PATTERNS
        # ====================================================
        #
        # Product/device/app signals should come BEFORE
        # generic payment words such as:
        #
        # "pay"
        # "price"
        # "paid"
        #
        # Example:
        #
        # "Can I pay £10 more to remove ads from Fire HD?"
        #
        # => product_issue
        # ====================================================

        product_patterns = [

            r"\bfire hd\b",
            r"\bfire tablet\b",
            r"\bfire tv\b",
            r"\bfirestick\b",
            r"\bfire stick\b",

            r"\bkindle\b",

            r"\balexa\b",
            r"\balexa app\b",

            r"\bamazon app\b",
            r"\bios app\b",
            r"\bandroid app\b",

            r"\bandroid tv\b",

            r"\btablet\b",
            r"\bdevice\b",

            r"\bapp\b",
            r"\bapplication\b",
            r"\bapplications\b",

            r"\bapplications library\b",

            r"\bvoice recognition\b",

            r"\bsubtitles?\b",

            r"\bcompatib",
            r"\bcompatible\b",

            r"\bslow\b.*\bapp\b",
            r"\bapp\b.*\bslow\b"
        ]

        if any(
            re.search(pattern, text)
            for pattern in product_patterns
        ):
            return "product_issue"


        # ====================================================
        # 5. REFUND / RETURN
        # ====================================================

        refund_patterns = [

            r"\brefund\b",
            r"\brefunds\b",
            r"\brefunded\b",

            r"\breturn\b",
            r"\breturned\b",

            r"\bmoney back\b",

            r"\breimburse\b",
            r"\breimbursement\b",

            r"\breembolso\b",
            r"\breembolsos\b",

            r"\bshipment back\b",
            r"\bsent the shipment back\b"
        ]

        if any(
            re.search(pattern, text)
            for pattern in refund_patterns
        ):
            return "refund_return"


        # ====================================================
        # 6. PRIME MEMBERSHIP
        # ====================================================
        #
        # This comes AFTER delivery.
        #
        # Therefore:
        #
        # "Prime delivery is late"
        # => delivery_issue
        #
        # "How much is Prime?"
        # => prime_membership
        # ====================================================

        prime_patterns = [

            r"\bprime membership\b",
            r"\bprime member\b",
            r"\bprime subscription\b",

            r"\bprime trial\b",
            r"\bfree trial\b",

            r"\bprime benefits?\b",
            r"\bprime reading\b",
            r"\bprime video\b",

            r"\bamazon prime\b",

            r"\bprime\b"
        ]

        if any(
            re.search(pattern, text)
            for pattern in prime_patterns
        ):
            return "prime_membership"


        # ====================================================
        # 7. PAYMENT
        # ====================================================
        #
        # Payment is intentionally checked AFTER product.
        #
        # This prevents:
        #
        # "pay £10 to remove Fire HD ads"
        #
        # from becoming payment_issue.
        # ====================================================

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

        if any(
            re.search(pattern, text)
            for pattern in payment_patterns
        ):
            return "payment_issue"


        # ====================================================
        # 8. MACHINE LEARNING FALLBACK
        # ====================================================
        #
        # If no high-confidence rule matched, allow the
        # Logistic Regression model to classify the message.
        # ====================================================

        return self.model.predict(
            [message]
        )[0]


    # ========================================================
    # PREDICT BATCH
    # ========================================================

    def predict_batch(self, messages):

        if not self.trained:
            self.train()

        predictions = []

        for message in messages:

            predictions.append(
                self.predict(message)
            )

        return predictions


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    classifier = IntentClassifier()

    classifier.train()


    # ========================================================
    # GOLDEN SET EVALUATION
    # ========================================================

    print("\n==============================")
    print("GOLDEN SET RESULTS")
    print("==============================")


    golden_df = pd.read_csv(
        GOLDEN_FILE
    )


    golden_df = golden_df.dropna(
        subset=[
            "customer_message",
            "intent"
        ]
    )


    X_test = golden_df[
        "customer_message"
    ]


    y_test = golden_df[
        "intent"
    ]


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


    # ========================================================
    # CLASSIFICATION REPORT
    # ========================================================

    print("\nClassification Report:")


    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )


    # ========================================================
    # EXAMPLE PREDICTIONS
    # ========================================================

    examples = [

        "My package has not arrived yet",

        "I need a refund for my order",

        "My Amazon Pay payment failed",

        "I cannot login to my account",

        "I want to cancel my order",

        "How much does Amazon Prime cost?",

        "My delivery is two days late",

        "My order says out for delivery",

        "The courier has not delivered my package",

        "My order says it was delivered but I have no package",

        "I need a reimbursement for my returned item",

        "My refund has not arrived",

        "I sent the shipment back and still need my refund",

        "Can I pay 10 more GBP to remove ads from my Fire HD?",

        "Why is the Alexa app moving so slow?",

        "What's the point of Prime if my delivery is late?",

        "Where is the applications library?"
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