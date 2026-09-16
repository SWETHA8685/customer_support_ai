import os
import json
import time
import pandas as pd
from openai import OpenAI

GOLDEN_FILE = "data/golden/golden_set.csv"
AGENT_RESULTS_FILE = "evaluation/agent_results.csv"
OUTPUT_FILE = "evaluation/llm_judge_results.csv"

MODEL = "gpt-5.6-luna"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

RUBRIC = """
You are evaluating an AI customer-support agent for an AmazonHelp customer.

Score the agent on five criteria from 0 to 2.

1. Intent correctness
2 = correct and specific intent
1 = related but not most specific
0 = clearly incorrect

2. Response relevance
2 = directly addresses the customer's issue
1 = partially relevant
0 = does not address the issue

3. Grounding
2 = consistent with the historical evidence
1 = mostly consistent but contains an unsupported assumption
0 = contradicts evidence or invents unsupported information

4. Helpfulness
2 = useful response or appropriate next step
1 = limited assistance
0 = not useful

5. Escalation appropriateness
2 = auto-handle/escalate decision is appropriate
1 = ambiguous/debatable
0 = clearly inappropriate

Critical failure:
Mark true when an unsafe auto-handle occurs for a case involving:
- payment or financial risk
- account access/security
- unresolved missing delivery
- repeated unsuccessful support
- explicit request for a human
- case-specific investigation/intervention

Return ONLY valid JSON.
"""


def judge_example(row):
    evidence = row.get("evidence", "")

    prompt = f"""
{RUBRIC}

CUSTOMER MESSAGE:
{row["customer_message"]}

EXPECTED INTENT:
{row["expected_intent"]}

AGENT PREDICTED INTENT:
{row["intent"]}

EXPECTED DECISION:
{row["expected_decision"]}

AGENT DECISION:
{row["decision"]}

AGENT RESPONSE:
{row["response"]}

HISTORICAL EVIDENCE:
{evidence}

Return this exact JSON structure:

{{
  "intent_score": 0,
  "relevance_score": 0,
  "grounding_score": 0,
  "helpfulness_score": 0,
  "escalation_score": 0,
  "overall_score": 0,
  "critical_failure": false,
  "reason": "short explanation"
}}
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt
    )

    text = response.output_text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(f"Judge returned invalid JSON:\n{text}")

        result = json.loads(text[start:end + 1])

    return result


def main():
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. "
            "Set it in PowerShell before running this script."
        )

    print("Loading agent evaluation results...")

    df = pd.read_csv(AGENT_RESULTS_FILE)

    print(f"Examples to judge: {len(df)}")
    print(f"Judge model: {MODEL}")

    results = []

    for i, row in df.iterrows():
        print(f"Judging {i + 1}/{len(df)}...", end=" ")

        try:
            result = judge_example(row)

            results.append({
                "customer_message": row["customer_message"],
                "expected_intent": row["expected_intent"],
                "intent": row["intent"],
                "expected_decision": row["expected_decision"],
                "decision": row["decision"],
                "response": row["response"],
                "intent_score": result["intent_score"],
                "relevance_score": result["relevance_score"],
                "grounding_score": result["grounding_score"],
                "helpfulness_score": result["helpfulness_score"],
                "escalation_score": result["escalation_score"],
                "overall_score": result["overall_score"],
                "critical_failure": result["critical_failure"],
                "reason": result["reason"]
            })

            print("OK")

        except Exception as e:
            print(f"ERROR: {e}")

        time.sleep(0.2)

    result_df = pd.DataFrame(results)

    result_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print("=" * 60)
    print("LLM JUDGE COMPLETE")
    print("=" * 60)

    if len(result_df) > 0:
        print(f"Examples judged: {len(result_df)}")
        print(
            "Average overall score:",
            round(result_df["overall_score"].mean(), 2)
        )
        print(
            "Critical failures:",
            int(result_df["critical_failure"].sum())
        )

        print()
        print("Score distribution:")
        print(
            result_df["overall_score"]
            .value_counts()
            .sort_index()
            .to_string()
        )

    print()
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()