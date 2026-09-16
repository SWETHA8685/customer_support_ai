import pandas as pd

FILE = "evaluation/evaluation_results.csv"

df = pd.read_csv(FILE)

print("=" * 60)
print("DECISION ANALYSIS")
print("=" * 60)

print("\nExpected decisions:")
print(df["expected_decision"].value_counts())

print("\nPredicted decisions:")
print(df["predicted_decision"].value_counts())

print("\nDecision mismatches:")
mismatches = df[
    df["expected_decision"] != df["predicted_decision"]
].copy()

print(f"\nTotal mismatches: {len(mismatches)}")

print("\nBreakdown by expected decision:")
print(
    mismatches["expected_decision"].value_counts()
)

print("\nBreakdown by intent:")
print(
    pd.crosstab(
        mismatches["expected_decision"],
        mismatches["predicted_intent"]
    )
)

print("\n" + "=" * 60)
print("FIRST 20 MISMATCHES")
print("=" * 60)

for i, row in mismatches.head(20).iterrows():

    print("\n----------------------------------------")

    print("Customer:")
    print(row["customer_message"])

    print("\nIntent:")
    print("Expected:", row["expected_intent"])
    print("Predicted:", row["predicted_intent"])

    print("\nDecision:")
    print("Expected:", row["expected_decision"])
    print("Predicted:", row["predicted_decision"])

    print("\nSimilarity:")
    print(round(row["similarity"], 3))

    print("\nReason:")
    print(row["reason"])

print("\nAnalysis complete.")