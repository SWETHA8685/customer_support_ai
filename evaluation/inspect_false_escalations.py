import pandas as pd


FILE = "evaluation/evaluation_results.csv"


def main():

    df = pd.read_csv(FILE)

    false_escalations = df[
        (df["expected_decision"] == "auto_handle") &
        (df["predicted_decision"] == "escalate")
    ]

    print("=" * 70)
    print("UNNECESSARY ESCALATIONS")
    print("=" * 70)

    print(
        f"\nTotal: {len(false_escalations)}"
    )

    for number, (_, row) in enumerate(
        false_escalations.iterrows(),
        start=1
    ):

        print("\n" + "-" * 70)

        print(f"CASE {number}")

        print("\nCustomer:")
        print(row["customer_message"])

        print("\nExpected intent:")
        print(row["expected_intent"])

        print("\nPredicted intent:")
        print(row["predicted_intent"])

        print("\nExpected decision:")
        print(row["expected_decision"])

        print("\nPredicted decision:")
        print(row["predicted_decision"])

        print("\nSimilarity:")
        print(round(row["similarity"], 3))

        print("\nReason:")
        print(row["reason"])

        print("\nSuggested response:")
        print(row["suggested_response"])


if __name__ == "__main__":
    main()