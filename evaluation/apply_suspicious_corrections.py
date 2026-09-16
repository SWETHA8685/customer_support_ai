import pandas as pd

GOLDEN_FILE = "data/golden/golden_set.csv"
REVIEW_FILE = "evaluation/suspicious_review.csv"

golden = pd.read_csv(GOLDEN_FILE)
review = pd.read_csv(REVIEW_FILE)

# Only apply rows explicitly approved by human review
approved = review[
    review["human_review"].astype(str).str.strip().str.upper() == "YES"
].copy()

print("Approved corrections:", len(approved))

changes = 0

for _, row in approved.iterrows():
    row_id = int(row["row_id"])

    # row_id is 1-based, while pandas uses 0-based indexing
    index = row_id - 1

    if index < 0 or index >= len(golden):
        print(f"WARNING: row_id {row_id} is outside golden set")
        continue

    old_intent = golden.at[index, "intent"]
    old_decision = golden.at[index, "decision"]

    new_intent = row["proposed_intent"]
    new_decision = row["proposed_decision"]

    if old_intent != new_intent or old_decision != new_decision:
        golden.at[index, "intent"] = new_intent
        golden.at[index, "decision"] = new_decision

        print(
            f"Row {row_id}: "
            f"{old_intent} / {old_decision} "
            f"-> {new_intent} / {new_decision}"
        )

        changes += 1

golden.to_csv(GOLDEN_FILE, index=False)

print()
print("Corrections applied:", changes)
print("Updated:", GOLDEN_FILE)