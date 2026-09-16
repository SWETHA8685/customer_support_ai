import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

GOLDEN_FILE = "data/golden/golden_set.csv"


def trivial_baseline(df):
    """
    Trivial baseline:
    - Always predict the majority intent.
    - Always escalate.
    """

    majority_intent = df["intent"].value_counts().idxmax()

    df = df.copy()

    df["predicted_intent"] = majority_intent
    df["predicted_decision"] = "escalate"

    return df, majority_intent


def main():
    print("=" * 60)
    print("TRIVIAL BASELINE")
    print("=" * 60)

    df = pd.read_csv(GOLDEN_FILE)

    print(f"Golden examples: {len(df)}")

    results, majority_intent = trivial_baseline(df)

    print(f"\nMajority intent: {majority_intent}")

    # ---------------------------------------------------------
    # INTENT
    # ---------------------------------------------------------

    intent_accuracy = accuracy_score(
        results["intent"],
        results["predicted_intent"]
    )

    print("\nIntent Accuracy:")
    print(f"{intent_accuracy:.3f}")

    print("\nClassification Report:")
    print(
        classification_report(
            results["intent"],
            results["predicted_intent"],
            zero_division=0
        )
    )

    # ---------------------------------------------------------
    # DECISION
    # ---------------------------------------------------------

    decision_accuracy = accuracy_score(
        results["decision"],
        results["predicted_decision"]
    )

    print("\nDecision Accuracy:")
    print(f"{decision_accuracy:.3f}")

    print("\nDecision Confusion Matrix:")

    labels = ["auto_handle", "escalate"]

    print(
        confusion_matrix(
            results["decision"],
            results["predicted_decision"],
            labels=labels
        )
    )

    # ---------------------------------------------------------
    # SAFETY
    # ---------------------------------------------------------

    expected_escalations = (
        results["decision"] == "escalate"
    ).sum()

    correct_escalations = (
        (results["decision"] == "escalate")
        &
        (results["predicted_decision"] == "escalate")
    ).sum()

    unsafe_auto_handles = (
        (results["decision"] == "escalate")
        &
        (results["predicted_decision"] == "auto_handle")
    ).sum()

    unnecessary_escalations = (
        (results["decision"] == "auto_handle")
        &
        (results["predicted_decision"] == "escalate")
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
    # SAVE RESULTS
    # ---------------------------------------------------------

    output_file = "evaluation/trivial_baseline_results.csv"

    results.to_csv(output_file, index=False)

    print("\nResults saved to:")
    print(output_file)


if __name__ == "__main__":
    main()