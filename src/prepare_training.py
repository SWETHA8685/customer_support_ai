import pandas as pd
import re
from pathlib import Path

INPUT_FILE = "data/processed/amazonhelp_conversations.csv"
OUTPUT_FILE = "data/processed/amazonhelp_training.csv"


def clean_text(text):
    text = str(text).lower()

    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"@\w+", " ", text)
    text = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def assign_intent(message):

    text = clean_text(message)

    # --------------------------------------------------------
    # DELIVERY NOT RECEIVED
    # --------------------------------------------------------

    if re.search(
        r"delivered but|"
        r"marked delivered|"
        r"says delivered|"
        r"not received|"
        r"didn.?t receive|"
        r"did not receive|"
        r"never received|"
        r"never arrived|"
        r"missing package|"
        r"missing parcel",
        text
    ):
        return "delivery_not_received"


    # --------------------------------------------------------
    # PAYMENT
    # --------------------------------------------------------

    if re.search(
        r"payment|"
        r"amazon pay|"
        r"credit card|"
        r"debit card|"
        r"gift card|"
        r"billing|"
        r"billed|"
        r"charged|"
        r"cashback|"
        r"coupon|"
        r"voucher|"
        r"transaction",
        text
    ):
        return "payment_issue"


    # --------------------------------------------------------
    # REFUND / RETURN
    # --------------------------------------------------------

    if re.search(
        r"refund|"
        r"refunded|"
        r"return|"
        r"returned|"
        r"money back|"
        r"reimburse",
        text
    ):
        return "refund_return"


    # --------------------------------------------------------
    # PRIME
    # --------------------------------------------------------

    if re.search(
        r"\bprime\b|"
        r"prime membership|"
        r"prime member|"
        r"prime subscription",
        text
    ):
        return "prime_membership"


    # --------------------------------------------------------
    # ACCOUNT
    # --------------------------------------------------------

    if re.search(
        r"account|"
        r"login|"
        r"log in|"
        r"sign in|"
        r"password|"
        r"verification|"
        r"verify",
        text
    ):
        return "account_issue"


    # --------------------------------------------------------
    # PRODUCT
    # --------------------------------------------------------

    if re.search(
        r"product|"
        r"item|"
        r"size|"
        r"colour|"
        r"color|"
        r"model|"
        r"broken|"
        r"damaged|"
        r"defective|"
        r"quality|"
        r"stock|"
        r"availability",
        text
    ):
        return "product_issue"


    # --------------------------------------------------------
    # ORDER
    # --------------------------------------------------------

    if re.search(
        r"order number|"
        r"order id|"
        r"order issue|"
        r"order problem|"
        r"wrong order|"
        r"cancel order|"
        r"cancelled order|"
        r"canceled order|"
        r"modify order|"
        r"change order|"
        r"ordered|"
        r"\border\b",
        text
    ):
        return "order_issue"


    # --------------------------------------------------------
    # DELIVERY
    # --------------------------------------------------------

    if re.search(
        r"delivery|"
        r"deliver|"
        r"shipping|"
        r"shipment|"
        r"package|"
        r"parcel|"
        r"arriv|"
        r"late|"
        r"delayed|"
        r"tracking|"
        r"tracked|"
        r"courier|"
        r"out for delivery",
        text
    ):
        return "delivery_issue"


    # --------------------------------------------------------
    # SERVICE COMPLAINT
    # --------------------------------------------------------

    if re.search(
        r"worst|"
        r"terrible|"
        r"horrible|"
        r"pathetic|"
        r"useless|"
        r"ridiculous|"
        r"awful|"
        r"angry|"
        r"disappoint|"
        r"complaint|"
        r"complain|"
        r"frustrated|"
        r"frustrating|"
        r"helpless|"
        r"no response|"
        r"no answer|"
        r"bad service|"
        r"bad support",
        text
    ):
        return "service_complaint"


    return "service_complaint"


print("Loading AmazonHelp conversations...")

df = pd.read_csv(INPUT_FILE)

print("Total conversations:", len(df))

print("\nCreating intent labels...")

df["intent"] = df["customer_message"].apply(assign_intent)

training = df[
    [
        "customer_message",
        "agent_response",
        "intent"
    ]
].copy()

training = training.dropna(
    subset=["customer_message"]
)

training = training[
    training["customer_message"]
    .astype(str)
    .str.strip()
    != ""
]

Path(OUTPUT_FILE).parent.mkdir(
    parents=True,
    exist_ok=True
)

training.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nTraining dataset created successfully!")

print("File:", OUTPUT_FILE)

print("Rows:", len(training))

print("\nIntent distribution:")

print(
    training["intent"].value_counts()
)

print("\nIntent percentages:")

print(
    training["intent"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
    .astype(str)
    + "%"
)