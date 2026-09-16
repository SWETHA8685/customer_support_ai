import pandas as pd
import os

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

GOLDEN_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "golden",
    "golden_set.csv"
)

OUTPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "golden",
    "golden_set_reviewed.csv"
)


def decide_from_message(message, intent):
    """
    Suggest an escalation decision based on the
    decision-labeling rubric.

    This is ONLY a review suggestion.
    The final golden-set label should be human-reviewed.
    """

    text = str(message).lower().strip()

    escalation_signals = [
        "no response",
        "no answer",
        "no answers",
        "no help",
        "no one helping",
        "nobody",
        "no one",
        "already contacted",
        "contacted before",
        "called before",
        "called support",
        "contacted support",
        "third time",
        "fourth time",
        "fifth time",
        "explaining it",
        "again",
        "still",
        "never received",
        "didn't receive",
        "did not receive",
        "not received",
        "lost",
        "missing",
        "complaint",
        "reclamation",
        "reimburse",
        "refund",
        "charged",
        "payment",
        "order number",
        "order #",
        "cancel",
        "replacement",
        "speak to someone",
        "talk to someone",
        "speak with someone",
        "talk with someone",
        "human",
        "representative",
        "supervisor",
        "customer service",
        "customer care",
        "helpline",
        "investigation",
        "urgent"
    ]

    if any(signal in text for signal in escalation_signals):
        return "escalate"

    return "auto_handle"


def main():

    print("=" * 70)
    print("GOLDEN SET DECISION REVIEW")
    print("=" * 70)

    print("\nLoading golden set...")

    df = pd.read_csv(GOLDEN_FILE)

    print(f"Total examples: {len(df)}")

    # ----------------------------------------------------------
    # Create suggested decision
    # ----------------------------------------------------------

    df["suggested_decision"] = df.apply(
        lambda row: decide_from_message(
            row["customer_message"],
            row["intent"]
        ),
        axis=1
    )

    # ----------------------------------------------------------
    # Mark disagreements
    # ----------------------------------------------------------

    df["needs_review"] = (
        df["decision"] != df["suggested_decision"]
    )

    # ----------------------------------------------------------
    # Save reviewed copy
    # ----------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    review_count = int(
        df["needs_review"].sum()
    )

    print(
        f"\nExamples needing manual review: {review_count}"
    )

    print(
        f"\nSaved review file:\n{OUTPUT_FILE}"
    )

    # ----------------------------------------------------------
    # Summary
    # ----------------------------------------------------------

    print("\nDecision distribution:")
    print(
        df["decision"].value_counts()
    )

    print("\nSuggested decision distribution:")
    print(
        df["suggested_decision"].value_counts()
    )

    # ----------------------------------------------------------
    # Show review examples
    # ----------------------------------------------------------

    review_df = df[
        df["needs_review"]
    ]

    print("\n" + "=" * 70)
    print("EXAMPLES NEEDING REVIEW")
    print("=" * 70)

    for index, row in review_df.iterrows():

        print("\n" + "-" * 70)

        print(
            f"Row: {index}"
        )

        print(
            f"Intent: {row['intent']}"
        )

        print(
            f"Current decision: {row['decision']}"
        )

        print(
            f"Suggested decision: {row['suggested_decision']}"
        )

        print(
            "\nCustomer message:"
        )

        print(
            row["customer_message"]
        )


if __name__ == "__main__":
    main()