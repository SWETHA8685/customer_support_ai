import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

RESULTS_FILE = os.path.join(
    PROJECT_ROOT,
    "evaluation",
    "evaluation_results.csv"
)


def main():

    df = pd.read_csv(RESULTS_FILE)

    print("\n" + "=" * 60)
    print("FINAL ERROR AND FAILURE-MODE ANALYSIS")
    print("=" * 60)

    # --------------------------------------------------
    # OVERALL COUNTS
    # --------------------------------------------------

    print("\nTotal examples:", len(df))

    intent_correct = (
        df["expected_intent"] ==
        df["predicted_intent"]
    )

    decision_correct = (
        df["expected_decision"] ==
        df["predicted_decision"]
    )

    print(
        "Intent errors:",
        (~intent_correct).sum()
    )

    print(
        "Decision errors:",
        (~decision_correct).sum()
    )

    # --------------------------------------------------
    # UNSAFE AUTO-HANDLES
    # --------------------------------------------------

    unsafe = df[
        (df["expected_decision"] == "escalate") &
        (df["predicted_decision"] == "auto_handle")
    ]

    print("\n" + "=" * 60)
    print("UNSAFE AUTO-HANDLES")
    print("=" * 60)

    print("Count:", len(unsafe))

    if len(unsafe) > 0:
        print(
            "\nBy predicted intent:"
        )
        print(
            unsafe["predicted_intent"]
            .value_counts()
        )

        print("\nCases:")

        for _, row in unsafe.iterrows():
            print("\n" + "-" * 50)
            print(
                "Customer:",
                row["customer_message"]
            )
            print(
                "Intent:",
                row["predicted_intent"]
            )
            print(
                "Similarity:",
                round(float(row["similarity"]), 3)
            )
            print(
                "Reason:",
                row["reason"]
            )

    # --------------------------------------------------
    # UNNECESSARY ESCALATIONS
    # --------------------------------------------------

    unnecessary = df[
        (df["expected_decision"] == "auto_handle") &
        (df["predicted_decision"] == "escalate")
    ]

    print("\n" + "=" * 60)
    print("UNNECESSARY ESCALATIONS")
    print("=" * 60)

    print("Count:", len(unnecessary))

    print(
        "\nBy predicted intent:"
    )

    print(
        unnecessary["predicted_intent"]
        .value_counts()
    )

    print(
        "\nAverage similarity:",
        round(
            unnecessary["similarity"].mean(),
            3
        )
    )

    # --------------------------------------------------
    # INTENT CONFUSIONS
    # --------------------------------------------------

    intent_errors = df[
        df["expected_intent"] !=
        df["predicted_intent"]
    ]

    print("\n" + "=" * 60)
    print("INTENT CONFUSIONS")
    print("=" * 60)

    print("Count:", len(intent_errors))

    if len(intent_errors) > 0:

        print("\nExpected -> Predicted:")

        confusion = (
            intent_errors
            .groupby(
                [
                    "expected_intent",
                    "predicted_intent"
                ]
            )
            .size()
            .sort_values(
                ascending=False
            )
        )

        print(confusion)

    # --------------------------------------------------
    # SIMILARITY BUCKET ANALYSIS
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("RETRIEVAL SIMILARITY ANALYSIS")
    print("=" * 60)

    bins = [-0.01, 0.30, 0.50, 0.70, 1.00]

    labels = [
        "0.00-0.30",
        "0.30-0.50",
        "0.50-0.70",
        "0.70-1.00"
    ]

    df["similarity_bucket"] = pd.cut(
        df["similarity"],
        bins=bins,
        labels=labels
    )

    print(
        df["similarity_bucket"]
        .value_counts()
        .sort_index()
    )

    # --------------------------------------------------
    # TOP FAILURE MODES
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("TOP FAILURE MODES FOR FINAL REPORT")
    print("=" * 60)

    print("""
1. Conservative escalation policy
   - Very high escalation recall (100.0%)
   - But many unnecessary escalations

2. Low retrieval similarity after leakage removal
   - Exact evaluation examples are excluded
   - This gives a more realistic retrieval evaluation

3. Ambiguous customer messages
   - Short or vague messages can be difficult to route

4. Intent overlap
   - Delivery, order, product, and refund issues can overlap

5. Historical response limitations
   - A retrieved historical response may not contain enough
     customer-specific context for safe automation
""")

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()