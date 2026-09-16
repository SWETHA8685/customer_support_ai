import pandas as pd

INPUT_FILE = "data/golden/golden_set.csv"
OUTPUT_FILE = "evaluation/suspicious_review.csv"

df = pd.read_csv(INPUT_FILE)

# Rows identified as likely inconsistent with our escalation rubric.
proposed_changes = {
    20: ("delivery_not_received", "escalate"),
    25: ("refund_return", "escalate"),
    38: ("service_complaint", "escalate"),
    75: ("delivery_issue", "escalate"),
    83: ("service_complaint", "escalate"),
    84: ("payment_issue", "escalate"),
    87: ("service_complaint", "escalate"),
    90: ("service_complaint", "escalate"),
    96: ("service_complaint", "escalate"),
    105: ("delivery_not_received", "escalate"),
    106: ("account_issue", "escalate"),
    111: ("service_complaint", "escalate"),
    113: ("service_complaint", "escalate"),
    127: ("delivery_issue", "escalate"),
    129: ("product_issue", "escalate"),
    131: ("service_complaint", "escalate"),
    134: ("product_issue", "escalate"),
    139: ("delivery_not_received", "escalate"),
    141: ("account_issue", "escalate"),
    145: ("service_complaint", "escalate"),
    148: ("service_complaint", "escalate"),
    155: ("product_issue", "escalate"),
    156: ("product_issue", "escalate"),
    158: ("product_issue", "escalate"),
    163: ("payment_issue", "escalate"),
    165: ("service_complaint", "escalate"),
    166: ("service_complaint", "escalate"),
    172: ("service_complaint", "escalate"),
    179: ("service_complaint", "escalate"),
    182: ("service_complaint", "escalate"),
    186: ("service_complaint", "escalate"),
    188: ("delivery_not_received", "escalate"),
}

rows = []

for row_id, (proposed_intent, proposed_decision) in proposed_changes.items():
    if row_id not in df.index:
        print(f"Warning: row {row_id} not found")
        continue

    row = df.loc[row_id]

    rows.append({
        "row_id": row_id,
        "customer_message": row["customer_message"],
        "current_intent": row["intent"],
        "current_decision": row["decision"],
        "proposed_intent": proposed_intent,
        "proposed_decision": proposed_decision,
        "human_review": ""
    })

review_df = pd.DataFrame(rows)

review_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print()
print("=" * 70)
print("SUSPICIOUS GOLDEN-SET REVIEW FILE CREATED")
print("=" * 70)
print(f"Rows for review: {len(review_df)}")
print(f"Output: {OUTPUT_FILE}")
print()
print("Open the CSV and fill the 'human_review' column:")
print("  YES = accept proposed correction")
print("  NO  = keep the existing label")
print()