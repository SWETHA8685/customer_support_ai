import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


FILE = "evaluation/evaluation_results.csv"


def main():

    df = pd.read_csv(FILE)

    expected = df["expected_decision"]
    predicted = df["predicted_decision"]

    print("=" * 60)
    print("DECISION METRICS")
    print("=" * 60)

    accuracy = accuracy_score(
        expected,
        predicted
    )

    precision = precision_score(
        expected,
        predicted,
        pos_label="escalate"
    )

    recall = recall_score(
        expected,
        predicted,
        pos_label="escalate"
    )

    f1 = f1_score(
        expected,
        predicted,
        pos_label="escalate"
    )

    print(f"\nAccuracy:  {accuracy:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"F1:        {f1:.3f}")

    print("\nConfusion Matrix:")
    print(
        confusion_matrix(
            expected,
            predicted,
            labels=[
                "auto_handle",
                "escalate"
            ]
        )
    )

    print("\n")
    print("=" * 60)
    print("DECISION DISTRIBUTION")
    print("=" * 60)

    print("\nExpected:")
    print(expected.value_counts())

    print("\nPredicted:")
    print(predicted.value_counts())

    print("\n")
    print("=" * 60)
    print("ERROR ANALYSIS")
    print("=" * 60)

    false_auto = df[
        (expected == "escalate") &
        (predicted == "auto_handle")
    ]

    false_escalate = df[
        (expected == "auto_handle") &
        (predicted == "escalate")
    ]

    print(
        f"\nUnsafe auto-handles: "
        f"{len(false_auto)}"
    )

    print(
        f"Unnecessary escalations: "
        f"{len(false_escalate)}"
    )

    print("\nUnsafe auto-handles by intent:")

    print(
        false_auto["predicted_intent"]
        .value_counts()
    )

    print("\nUnnecessary escalations by intent:")

    print(
        false_escalate["predicted_intent"]
        .value_counts()
    )


if __name__ == "__main__":
    main()