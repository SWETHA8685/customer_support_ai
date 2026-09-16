
import pandas as pd
import re
from pathlib import Path


# ============================================================
# FILE PATHS
# ============================================================

INPUT_FILE = "data/processed/amazonhelp_conversations.csv"
OUTPUT_FILE = "data/processed/amazonhelp_training.csv"


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    """
    Clean a customer message before intent classification.
    """

    text = str(text).lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)

    # Remove Twitter mentions
    text = re.sub(r"@\w+", " ", text)

    # Keep letters, numbers and spaces
    text = re.sub(
        r"[^a-zA-ZÀ-ÿ0-9\s]",
        " ",
        text
    )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ============================================================
# INTENT ASSIGNMENT
# ============================================================

def assign_intent(message):
    """
    Assign one of the nine support intents.

    The rules are ordered from the most specific cases
    to the more general cases to reduce overlap.
    """

    text = clean_text(message)

    # --------------------------------------------------------
    # 1. DELIVERY NOT RECEIVED
    # --------------------------------------------------------
    # This must come before generic delivery/order rules.
    #
    # Examples:
    # "says delivered but I didn't receive it"
    # "package was marked delivered"
    # "never received my parcel"
    # --------------------------------------------------------

    if re.search(
        r"delivered but|"
        r"says delivered|"
        r"marked delivered|"
        r"shows delivered|"
        r"not received|"
        r"didn.?t receive|"
        r"did not receive|"
        r"never arrived|"
        r"never received|"
        r"missing package|"
        r"missing parcel|"
        r"package.*missing|"
        r"parcel.*missing",
        text
    ):
        return "delivery_not_received"


    # --------------------------------------------------------
    # 2. REFUND / RETURN
    # --------------------------------------------------------
    # Explicit refund or return requests.
    # --------------------------------------------------------

    if re.search(
        r"refund|"
        r"refunded|"
        r"return item|"
        r"return product|"
        r"return my|"
        r"returned item|"
        r"returned product|"
        r"money back|"
        r"moneyback|"
        r"reimburse|"
        r"reimbursement",
        text
    ):
        return "refund_return"


    # --------------------------------------------------------
    # 3. PAYMENT
    # --------------------------------------------------------
    # Explicit payment and billing problems.
    # --------------------------------------------------------

    if re.search(
        r"payment failed|"
        r"payment failure|"
        r"payment issue|"
        r"payment problem|"
        r"amazon pay|"
        r"credit card|"
        r"debit card|"
        r"gift card|"
        r"giftcard|"
        r"billing|"
        r"billed|"
        r"charged twice|"
        r"double charged|"
        r"cashback|"
        r"coupon|"
        r"voucher|"
        r"transaction failed|"
        r"transaction declined|"
        r"card declined|"
        r"payment declined",
        text
    ):
        return "payment_issue"


    # --------------------------------------------------------
    # 4. PRIME MEMBERSHIP
    # --------------------------------------------------------

    if re.search(
        r"\bprime\b|"
        r"prime membership|"
        r"prime member|"
        r"prime subscription|"
        r"prime day",
        text
    ):
        return "prime_membership"


    # --------------------------------------------------------
    # 5. ACCOUNT
    # --------------------------------------------------------

    if re.search(
        r"account|"
        r"login|"
        r"log in|"
        r"sign in|"
        r"password|"
        r"locked out|"
        r"suspended account|"
        r"closed account|"
        r"verification|"
        r"verify my account",
        text
    ):
        return "account_issue"


    # --------------------------------------------------------
    # 6. PRODUCT
    # --------------------------------------------------------
    # Product-specific problems are checked before generic
    # order-related words.
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
        r"poor quality|"
        r"quality issue|"
        r"availability|"
        r"available|"
        r"out of stock|"
        r"stock",
        text
    ):
        return "product_issue"


    # --------------------------------------------------------
    # 7. ORDER
    # --------------------------------------------------------

    if re.search(
        r"order number|"
        r"order id|"
        r"order issue|"
        r"order problem|"
        r"wrong order|"
        r"wrong item|"
        r"cancel order|"
        r"cancelled order|"
        r"canceled order|"
        r"modify order|"
        r"change order|"
        r"ordered|"
        r"preorder|"
        r"\border\b",
        text
    ):
        return "order_issue"


    # --------------------------------------------------------
    # 8. DELIVERY
    # --------------------------------------------------------
    # Generic delivery/shipping/tracking cases.
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
    # 9. SERVICE COMPLAINT
    # --------------------------------------------------------
    # Only explicit complaint/frustration signals.
    #
    # We deliberately do NOT classify every support request
    # as a complaint.
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
        r"customer service.*bad|"
        r"support.*bad",
        text
    ):
        return "service_complaint"


    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    return "service_complaint"


# ============================================================
# LOAD AMAZONHELP CONVERSATIONS
# ============================================================

print("Loading AmazonHelp conversations...")

df = pd.read_csv(
    INPUT_FILE
)

print(
    "Total conversations:",
    len(df)
)


# ============================================================
# CREATE WEAK INTENT LABELS
# ============================================================

print("\nCreating intent labels...")

df["intent"] = df[
    "customer_message"
].apply(
    assign_intent
)


# ============================================================
# KEEP REQUIRED COLUMNS
# ============================================================

training = df[
    [
        "customer_message",
        "agent_response",
        "intent"
    ]
].copy()


# ============================================================
# REMOVE EMPTY CUSTOMER MESSAGES
# ============================================================

training = training.dropna(
    subset=["customer_message"]
)

training = training[
    training[
        "customer_message"
    ].astype(str).str.strip() != ""
]


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

Path(
    OUTPUT_FILE
).parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SAVE TRAINING DATA
# ============================================================

training.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# RESULTS
# ============================================================

print(
    "\nTraining dataset created successfully!"
)

print(
    "File:",
    OUTPUT_FILE
)

print(
    "Rows:",
    len(training)
)


print(
    "\nIntent distribution:"
)

print(
    training["intent"].value_counts()
)


# ============================================================
# SANITY CHECK
# ============================================================

print(
    "\nIntent percentages:"
)

print(
    (
        training["intent"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
        .astype(str)
        + "%"
    )
)

