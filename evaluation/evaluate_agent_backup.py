import sys
import os

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# Add src folder to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")

sys.path.insert(0, SRC_PATH)

from agent import SupportAgent


GOLDEN_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "golden",
    "golden_set.csv"
)


def main():

    print("=" * 60)
    print("HIVER SDE SUPPORT AGENT EVALUATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # LOAD GOLDEN SET
    # ---------------------------------------------------------

    print("\nLoading golden set...")

    df = pd.read_csv(GOLDEN_FILE)

    df = df.dropna(
        subset=[
            "customer_message",
            "intent",
            "decision"
        ]
    )

    print(f"Golden examples: {len(df)}")

    # ---------------------------------------------------------
    # INITIALIZE AGENT
    # ---------------------------------------------------------

    print("\nInitializing support agent...")

    agent = SupportAgent()

    # ---------------------------------------------------------
    # EVALUATION
    # ---------------------------------------------------------

    predicted_intents = []
    predicted_decisions = []
    results = []

    print("\nRunning evaluation...")
    print("=" * 60)

    for index, row in df.iterrows():

        message = str(row["customer_message"])

        result = agent.handle(message)

        predicted_intents.append(
            result["intent"]
        )

        predicted_decisions.append(
            result["decision"]
        )

        similarity = 0.0

        if result.get("evidence") is not None:
            similarity = result["evidence"].get(
                "similarity",
                0.0
            )

        results.append({

            "customer_message": message,

            "expected_intent":
                row["intent"],

            "predicted_intent":
                result["intent"],

            "expected_decision":
                row["decision"],

            "predicted_decision":
                result["decision"],

            "similarity":
                similarity,

            "suggested_response":
                result["suggested_response"],

            "reason":
                result["reason"]
        })

        if (index + 1) % 25 == 0:

            print(
                f"Processed "
                f"{index + 1}/{len(df)}"
            )

    # ---------------------------------------------------------
    # INTENT RESULTS
    # ---------------------------------------------------------

    intent_accuracy = accuracy_score(
        df["intent"],
        predicted_intents
    )

    print("\n")
    print("=" * 60)
    print("INTENT CLASSIFICATION RESULTS")
    print("=" * 60)

    print(
        f"\nIntent Accuracy: "
        f"{intent_accuracy:.3f}"
    )

    print("\nClassification Report:")

    print(
        classification_report(
            df["intent"],
            predicted_intents,
            zero_division=0
        )
    )

    # ---------------------------------------------------------
    # DECISION RESULTS
    # ---------------------------------------------------------

    decision_accuracy = accuracy_score(
        df["decision"],
        predicted_decisions
    )

    print("=" * 60)
    print("AUTO-HANDLE / ESCALATE RESULTS")
    print("=" * 60)

    print(
        f"\nDecision Accuracy: "
        f"{decision_accuracy:.3f}"
    )

    print("\nDecision Confusion Matrix:")

    print(
        confusion_matrix(
            df["decision"],
            predicted_decisions,
            labels=[
                "auto_handle",
                "escalate"
            ]
        )
    )

    # ---------------------------------------------------------
    # DECISION SAFETY METRICS
    # ---------------------------------------------------------

    expected_escalations = (
        df["decision"] == "escalate"
    ).sum()

    correct_escalations = (
        (
            (df["decision"] == "escalate") &
            (
                pd.Series(predicted_decisions)
                .values == "escalate"
            )
        )
    ).sum()

    unsafe_auto_handles = (
        (
            (df["decision"] == "escalate") &
            (
                pd.Series(predicted_decisions)
                .values == "auto_handle"
            )
        )
    ).sum()

    unnecessary_escalations = (
        (
            (df["decision"] == "auto_handle") &
            (
                pd.Series(predicted_decisions)
                .values == "escalate"
            )
        )
    ).sum()

    print("\nDecision Safety Metrics:")

    print(
        f"Expected escalations: "
        f"{expected_escalations}"
    )

    print(
        f"Correct escalations: "
        f"{correct_escalations}"
    )

    if expected_escalations > 0:

        escalation_recall = (
            correct_escalations /
            expected_escalations
        )

        print(
            f"Escalation recall: "
            f"{escalation_recall:.3f}"
        )

    print(
        f"Unsafe auto-handles: "
        f"{unsafe_auto_handles}"
    )

    print(
        f"Unnecessary escalations: "
        f"{unnecessary_escalations}"
    )

    # ---------------------------------------------------------
    # RETRIEVAL RESULTS
    # ---------------------------------------------------------

    similarities = pd.Series(
        [
            result["similarity"]
            for result in results
        ]
    )

    print("\n")
    print("=" * 60)
    print("RETRIEVAL RESULTS")
    print("=" * 60)

    print(
        f"\nAverage similarity: "
        f"{similarities.mean():.3f}"
    )

    print(
        f"Median similarity: "
        f"{similarities.median():.3f}"
    )

    print(
        f"Similarity >= 0.70: "
        f"{(similarities >= 0.70).mean():.1%}"
    )

    print(
        f"Similarity >= 0.50: "
        f"{(similarities >= 0.50).mean():.1%}"
    )

    # ---------------------------------------------------------
    # SAVE RESULTS
    # ---------------------------------------------------------

    results_df = pd.DataFrame(results)

    output_file = os.path.join(
        PROJECT_ROOT,
        "evaluation",
        "evaluation_results.csv"
    )

    results_df.to_csv(
        output_file,
        index=False
    )

    print("\n")
    print("=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)

    print(
        f"\nResults saved to:\n"
        f"{output_file}"
    )


if __name__ == "__main__":
    main()