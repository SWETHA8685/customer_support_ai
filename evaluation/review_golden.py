import pandas as pd
import os
import re


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "golden",
    "golden_set_reviewed.csv"
)

OUTPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "golden",
    "golden_set_final.csv"
)


# ============================================================
# ESCALATION SIGNALS
# ============================================================

STRONG_ESCALATION_SIGNALS = [
    "speak to someone",
    "talk to someone",
    "speak with someone",
    "talk with someone",
    "speak to a human",
    "talk to a human",
    "human",
    "representative",
    "supervisor",
    "manager",
    "escalate",
    "escalated",
    "escalation",

    "already contacted",
    "contacted before",
    "called before",
    "called support",
    "contacted support",

    "no response",
    "no answer",
    "no answers",
    "no help",
    "nobody helping",
    "no one helping",
    "no one does anything",
    "nobody does anything",

    "third time",
    "fourth time",
    "fifth time",
    "3rd time",
    "4th time",
    "5th time",

    "investigation",
    "complaint",
    "repeated complaint",
    "recurring complaint",

    "package was delivered",
    "marked delivered",
    "showing delivered",
    "says delivered",
    "never received",
    "didn't receive",
    "did not receive",
    "not received",
]


# ============================================================
# INTENT-SPECIFIC DECISION RULES
# ============================================================

def determine_decision(message, intent):

    text = str(message).lower().strip()

    # --------------------------------------------------------
    # Strong escalation signals apply to every intent
    # --------------------------------------------------------

    for signal in STRONG_ESCALATION_SIGNALS:

        if signal in text:
            return "escalate"

    # --------------------------------------------------------
    # DELIVERY NOT RECEIVED
    # --------------------------------------------------------

    if intent == "delivery_not_received":

        return "escalate"

    # --------------------------------------------------------
    # ACCOUNT ISSUES
    #
    # Routine account questions can be auto-handled.
    # Access/security/problem cases escalate.
    # --------------------------------------------------------

    if intent == "account_issue":

        account_escalation = [
            "can't access",
            "cannot access",
            "can't login",
            "cannot login",
            "locked",
            "hacked",
            "stolen",
            "security",
            "password",
            "unauthorized",
            "not my account",
        ]

        if any(x in text for x in account_escalation):
            return "escalate"

        return "auto_handle"

    # --------------------------------------------------------
    # PAYMENT
    #
    # Actual payment failures, deductions or missing money
    # require human intervention.
    # Simple informational questions can be automated.
    # --------------------------------------------------------

    if intent == "payment_issue":

        payment_escalation = [
            "charged",
            "charge",
            "money deducted",
            "money taken",
            "deducted",
            "transaction failed",
            "transaction has failed",
            "payment failed",
            "paid twice",
            "double charged",
            "cashback",
            "money back",
            "refund",
            "credit missing",
            "gift card",
        ]

        if any(x in text for x in payment_escalation):
            return "escalate"

        return "auto_handle"

    # --------------------------------------------------------
    # REFUND / RETURN
    # --------------------------------------------------------

    if intent == "refund_return":

        refund_escalation = [
            "refund missing",
            "refund not received",
            "refund hasn't",
            "refund has not",
            "money back",
            "return failed",
            "return problem",
            "return pick",
            "return pickup",
            "wrong refund",
            "charged",
        ]

        if any(x in text for x in refund_escalation):
            return "escalate"

        # Simple return questions can be handled automatically
        return "auto_handle"

    # --------------------------------------------------------
    # PRIME
    # --------------------------------------------------------

    if intent == "prime_membership":

        prime_escalation = [
            "charged",
            "charge",
            "wrong charge",
            "refund",
            "cancel",
            "cancelled",
            "canceled",
            "renewal",
            "renewed",
            "not working",
            "problem",
            "issue",
            "still",
            "lost",
            "didn't arrive",
            "did not arrive",
            "not arrived",
            "never arrived",
        ]

        if any(x in text for x in prime_escalation):
            return "escalate"

        return "auto_handle"

    # --------------------------------------------------------
    # ORDER
    # --------------------------------------------------------

    if intent == "order_issue":

        order_escalation = [
            "cancel",
            "cancelled",
            "canceled",
            "change my order",
            "modify",
            "wrong item",
            "missing item",
            "not received",
            "replacement",
            "refund",
            "lost",
            "where is my",
            "where's my",
        ]

        if any(x in text for x in order_escalation):
            return "escalate"

        # Providing an order number/details is not automatically
        # an escalation.
        return "auto_handle"

    # --------------------------------------------------------
    # DELIVERY
    # --------------------------------------------------------

    if intent == "delivery_issue":

        delivery_escalation = [
            "wrong address",
            "wrong location",
            "wrong place",
            "delivered to",
            "sent to",
            "lost",
            "missing",
            "never arrived",
            "didn't arrive",
            "did not arrive",
            "not arrived",
            "can't deliver",
            "cannot deliver",
            "unable to deliver",
            "delivery guy",
            "courier",
            "delivery person",
            "damaged",
            "breaks my",
            "broke my",
            "multiple times",
            "second time",
            "twice",
        ]

        if any(x in text for x in delivery_escalation):
            return "escalate"

        # Simple delivery-status/date questions
        return "auto_handle"

    # --------------------------------------------------------
    # PRODUCT
    # --------------------------------------------------------

    if intent == "product_issue":

        product_escalation = [
            "defective",
            "broken",
            "damaged",
            "doesn't work",
            "doesnt work",
            "not working",
            "missing",
            "wrong product",
            "different product",
            "faulty",
            "replacement",
            "refund",
            "return",
        ]

        if any(x in text for x in product_escalation):
            return "escalate"

        return "auto_handle"

    # --------------------------------------------------------
    # SERVICE COMPLAINT
    # --------------------------------------------------------

    if intent == "service_complaint":

        service_escalation = [
            "no response",
            "no answer",
            "no help",
            "nobody",
            "no one",
            "already contacted",
            "contacted before",
            "called before",
            "third time",
            "fourth time",
            "fifth time",
            "3rd time",
            "4th time",
            "5th time",
            "speak to",
            "talk to",
            "supervisor",
            "representative",
            "human",
            "escalate",
            "investigation",
            "repeated complaint",
            "recurring complaint",
        ]

        if any(x in text for x in service_escalation):
            return "escalate"

        return "auto_handle"

    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    return "auto_handle"


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("AUTOMATIC GOLDEN SET DECISION CORRECTION")
    print("=" * 70)

    # --------------------------------------------------------
    # Check file
    # --------------------------------------------------------

    if not os.path.exists(INPUT_FILE):

        print("\nERROR: File not found:")
        print(INPUT_FILE)

        return

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    df = pd.read_csv(INPUT_FILE)

    print(
        f"\nLoaded examples: {len(df)}"
    )

    # --------------------------------------------------------
    # Generate corrected decisions
    # --------------------------------------------------------

    df["final_decision"] = df.apply(
        lambda row: determine_decision(
            row["customer_message"],
            row["intent"]
        ),
        axis=1
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    print("\nOriginal decision distribution:")
    print(
        df["decision"].value_counts()
    )

    print("\nCorrected decision distribution:")
    print(
        df["final_decision"].value_counts()
    )

    changed = (
        df["decision"]
        != df["final_decision"]
    ).sum()

    print(
        f"\nDecisions changed automatically: {changed}"
    )

    print(
        "\nFinal file:"
    )

    print(
        OUTPUT_FILE
    )

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()