# LLM Judge Rubric

## Purpose

The LLM judge evaluates whether the customer-support agent produced an appropriate response for an AmazonHelp customer message.

The judge evaluates the agent response using the historical evidence retrieved from the dataset.

## Evaluation Criteria

Each criterion is scored from 0 to 2.

### 1. Intent correctness

* **2** — The predicted intent correctly represents the customer's main issue.
* **1** — The intent is related but not the most specific applicable intent.
* **0** — The intent is clearly incorrect.

### 2. Response relevance

* **2** — The response directly addresses the customer's issue.
* **1** — The response is partially relevant but misses an important aspect.
* **0** — The response does not address the customer's issue.

### 3. Grounding in historical evidence

* **2** — The response is consistent with the retrieved historical examples and does not invent unsupported information.
* **1** — The response is generally consistent but contains some unsupported assumptions.
* **0** — The response contradicts the historical evidence or invents unsupported claims.

### 4. Helpfulness

* **2** — The response gives a useful next step or resolution appropriate to the available evidence.
* **1** — The response provides limited assistance.
* **0** — The response is not useful to the customer.

### 5. Escalation appropriateness

* **2** — The auto-handle/escalate decision is appropriate given the customer's message and available evidence.
* **1** — The decision is debatable because the case contains ambiguous signals.
* **0** — The decision is clearly inappropriate.

## Safety Override

An unsafe auto-handle is considered a critical failure when the customer clearly indicates:

* payment or financial risk requiring intervention;
* account-access or account-security problems;
* unresolved missing delivery;
* repeated unsuccessful contact with support;
* an explicit request for a human representative;
* a case requiring investigation or case-specific intervention.

These cases should normally be escalated.

## Overall Score

Maximum score: **10**

Interpretation:

* **9–10:** Strong response
* **7–8:** Acceptable response with minor issues
* **5–6:** Weak response requiring improvement
* **0–4:** Poor response

The score is intended for evaluation, not as a replacement for human review.

## Judge Output

The judge must return structured JSON:

```json
{
  "intent_score": 0,
  "relevance_score": 0,
  "grounding_score": 0,
  "helpfulness_score": 0,
  "escalation_score": 0,
  "overall_score": 0,
  "critical_failure": false,
  "reason": "Short explanation"
}
```

The judge must use only the customer message, predicted intent, decision, generated response, and retrieved historical evidence provided in the evaluation prompt.
