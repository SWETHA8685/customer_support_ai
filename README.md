# AI Customer Support Agent

An AI-assisted customer support agent built for the **Customer Support on Twitter (TWCS)** dataset, using **AmazonHelp** conversations as the target brand.

The system demonstrates three core tasks:

1. **Intent classification**
2. **Grounded response drafting using historical support conversations**
3. **Auto-handle vs. escalate decision-making**

The project was developed as part of the **Hiver SDE Intern take-home assignment**.

---

## 1. Problem Framing

Customer-support automation should not only produce a plausible reply. A useful support system should also determine **when automation is safe and when a human agent should take over**.

For this project, I focused on AmazonHelp and defined the workflow as:

```text
Customer Message
       ↓
Intent Classification
       ↓
Historical Case Retrieval
       ↓
Safety / Handling Decision
       ↓
Grounded Response
       ↓
Auto-handle OR Escalate
```

The system is designed around a conservative principle:

> A response should be grounded in previously observed AmazonHelp support behavior, and cases with insufficient evidence or higher-risk signals should be escalated.

The implementation uses historical customer-support conversations rather than generating completely unsupported answers.

---

## 2. What "Good" Means

For an AmazonHelp-style support workflow, I consider the following important:

### Intent classification

The customer issue should be assigned to the correct support category.

### Grounded responses

A suggested response should be based on a relevant historical support interaction rather than unsupported information.

### Appropriate escalation

The system should avoid automatically handling cases that appear unresolved, sensitive, ambiguous, or likely to require account-specific investigation.

### Traceability

For an automatically handled case, the system should expose the historical evidence used to support the response.

### Honest uncertainty

High similarity between two messages is not by itself proof that the same resolution is appropriate. This is particularly important for complaints, payment problems, delivery problems, and account-specific cases.

---

## 3. What I Chose Not to Build

This project is intentionally a prototype rather than a production customer-support platform.

I did **not** build:

* A production Amazon account integration
* Real order lookup
* Real payment processing
* Real refund execution
* Real customer authentication
* Direct communication with customers
* A production LLM serving infrastructure
* Automatic execution of account-specific support actions
* A full enterprise ticketing system
* Real-time Twitter/X integration

The system therefore produces a **suggested support response and handling decision**, rather than performing an actual customer-support action.

---

## 4. System Architecture

```text
                    ┌─────────────────────┐
                    │ Customer Message    │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Intent Classifier   │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Historical Retriever│
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Safety Decision     │
                    │                     │
                    │ Auto-handle         │
                    │       OR            │
                    │ Escalate            │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Suggested Response  │
                    └─────────────────────┘
```

The implementation retrieves the top historical cases for the predicted intent and uses the strongest matching case as evidence.

When there is no sufficiently similar historical evidence, the system escalates instead of producing a grounded automated response.

---

## 5. Supported Intents

The current classifier uses nine support intents:

```text
account_issue
delivery_issue
delivery_not_received
order_issue
payment_issue
prime_membership
product_issue
refund_return
service_complaint
```

These categories cover common AmazonHelp support patterns such as delivery problems, refunds, payment issues, account problems, Prime questions, product problems, and service complaints.

---

## 6. Dataset

The project uses the **Customer Support on Twitter (TWCS)** dataset.

The implementation focuses on the `AmazonHelp` support account.

The processed conversation representation contains:

```text
customer_tweet_id
customer_id
customer_message
customer_created_at
agent_tweet_id
agent_response
```

The local processed AmazonHelp dataset contains approximately:

```text
168,814 historical conversations
```

The original TWCS dataset is intentionally **not committed to this repository** because of its large size.

Raw data is excluded through `.gitignore`.

---

## 7. Data Preparation

The raw TWCS dataset should be downloaded separately.

Place the dataset at:

```text
data/raw/twcs.csv
```

The raw dataset should not be committed to GitHub.

The AmazonHelp conversations can then be prepared using the scripts in `src/`.

The resulting processed dataset is used by the classifier and historical retriever.

---

## 8. Golden Evaluation Set

A manually reviewed golden set was created to evaluate the system.

The main evaluation run reported in this repository contains:

```text
200 examples
```

Each example contains customer-support information including:

```text
customer_message
agent_response
intent
decision
```

The project also contains manual-review artifacts used during the review process.

The review workflow tracks:

```text
customer_message
agent_response
intent
decision
manual_review_status
```

This was used to inspect difficult and potentially incorrect examples before evaluating the system.

---

## 9. Labeling Approach

The golden set was designed around two separate labels:

### Intent

The customer's primary support problem.

Examples:

```text
"My package has not arrived yet"
→ delivery_not_received

"I need a refund for my order"
→ refund_return

"My Amazon Pay payment failed"
→ payment_issue

"I cannot login to my account"
→ account_issue
```

### Decision

Whether the case should be:

```text
auto_handle
```

or:

```text
escalate
```

The decision label is intended to represent whether an automated response would be appropriate given the information available in the customer message.

---

## 10. Evaluation Methodology

The evaluation measures three different parts of the pipeline:

### A. Intent classification

Measured using:

* Accuracy
* Precision
* Recall
* F1-score
* Macro average
* Weighted average

### B. Handling decision

Measured using:

* Decision accuracy
* Confusion matrix

### C. Retrieval

Measured using:

* Average similarity
* Median similarity
* Percentage above similarity thresholds

This separates classification quality from retrieval quality and from the final automation decision.

---

# 11. Results

The main documented evaluation run used:

```text
Golden examples:             200
Historical conversations:    168,814
```

The recorded results were:

| Metric                       |    Result |
| ---------------------------- | --------: |
| Intent Accuracy              | **96.0%** |
| Macro F1                     | **95.0%** |
| Weighted F1                  | **96.0%** |
| Decision Accuracy            | **71.5%** |
| Average Retrieval Similarity | **0.958** |
| Median Retrieval Similarity  | **1.000** |
| Similarity ≥ 0.70            | **95.0%** |

The evaluation log reports 0.960 intent accuracy and 0.715 decision accuracy for the documented run.

### Classification report

| Intent                | Precision | Recall |   F1 |
| --------------------- | --------: | -----: | ---: |
| account_issue         |      1.00 |   1.00 | 1.00 |
| delivery_issue        |      1.00 |   0.88 | 0.94 |
| delivery_not_received |      0.83 |   1.00 | 0.91 |
| order_issue           |      1.00 |   0.90 | 0.95 |
| payment_issue         |      0.92 |   0.92 | 0.92 |
| prime_membership      |      1.00 |   1.00 | 1.00 |
| product_issue         |      0.93 |   1.00 | 0.96 |
| refund_return         |      0.90 |   0.90 | 0.90 |
| service_complaint     |      0.97 |   1.00 | 0.98 |

The largest class in this evaluation was `service_complaint`, with 84 examples, while several other intents had substantially smaller support. Therefore the overall 96% accuracy should not be interpreted as equally reliable performance across all intents.

---

# 12. Auto-handle vs Escalate

The handling decision is deliberately treated as a separate problem from intent classification.

The documented evaluation produced:

```text
Decision Accuracy: 0.715
```

Confusion matrix:

```text
[[84 10]
 [47 59]]
```

This shows that the decision problem is considerably harder than intent classification.

The system therefore does not treat a correct intent prediction as sufficient evidence for automatic handling.

---

# 13. Retrieval and Leakage Control

Historical retrieval is used to ground suggested responses.

For example, for:

```text
My package says delivered but I never received it.
```

the retriever returned historical delivery-not-received examples with similarities around:

```text
0.717
0.698
0.682
```

and matching intent:

```text
delivery_not_received
```

This provides an interpretable evidence trail for the suggested response.

To reduce evaluation leakage, the retrieval process removes golden-set examples from the retrieval index.

The documented retrieval run shows:

```text
Historical conversations before leakage removal: 168,814
Golden examples removed from retrieval index:       248
Historical conversations available:              168,566
```

The removal step is important because otherwise a golden example could retrieve itself or an extremely close duplicate and artificially inflate evaluation results.

---

# 14. Baselines

The repository includes baseline evaluation scripts:

```text
evaluation/evaluate_baselines.py
evaluation/evaluate_simple_baseline.py
evaluation/baselines.py
evaluation/trivial_baseline_results.csv
evaluation/simple_baseline_results.csv
```

The intended comparison is:

```text
Trivial baseline
        ↓
Simple baseline
        ↓
Proposed support agent
```

The baseline results should be regenerated using the repository scripts rather than relying on undocumented numbers.

Run:

```powershell
python evaluation\evaluate_baselines.py
```

and:

```powershell
python evaluation\evaluate_simple_baseline.py
```

The resulting CSV files provide the baseline measurements used for comparison.

---

# 15. Response Quality Evaluation

Response quality is treated separately from intent accuracy.

The repository includes:

```text
evaluation/LLM_JUDGE_RUBRIC.md
evaluation/evaluate_llm_judge.py
```

The intended judge dimensions are based on properties such as:

* Relevance to the customer's issue
* Grounding in available evidence
* Helpfulness
* Safety
* Appropriateness of escalation
* Avoiding unsupported claims

The LLM judge should be interpreted as an additional quality signal rather than ground truth.

LLM-based evaluation can vary with the judge model, prompt, and evaluation setup.

---

# 16. What Is Misleading About My Headline Number?

The headline number of **96% intent accuracy** is useful, but it is not the complete picture.

There are several reasons it can be misleading:

### 1. The golden set contains only 200 examples

A 200-example evaluation is useful for a prototype but is not representative of every possible AmazonHelp interaction.

### 2. The classes are imbalanced

`service_complaint` accounts for 84 of the 200 examples, while some other classes have only 4–13 examples.

Therefore the aggregate accuracy can hide weaker behavior on smaller classes.

### 3. Classification is easier than automation

The documented intent accuracy is 96%, while the handling-decision accuracy is 71.5%.

A system can understand what a customer is asking while still making the wrong decision about whether automation is safe.

### 4. Retrieval similarity is not proof of resolution correctness

A similarity score of 1.0 means the retrieved text is very similar according to the retrieval representation. It does not prove that the same resolution should be applied to the new customer.

### 5. Historical responses may contain context that is unavailable

The original support agent may have had access to account or order information that is not present in the customer's public message.

Therefore the system should not assume that a historically successful response is always safe to reuse.

### 6. The decision task is the more operationally important metric

For production support automation, a wrong auto-handle decision can be more costly than a wrong intent label.

For this reason, the 96% classification accuracy should be read together with the 71.5% decision accuracy and the failure analysis below.

---

# 17. Failure Analysis

The evaluation surfaced several recurring failure patterns.

## Failure 1 — Strong similarity but unsafe case

A customer message can have extremely high similarity to a historical case while still requiring human review.

Example:

```text
your cust.service just implied that my missing items are my fault
for living somewhere unsafe. Poor people dont deserve to get mail?
```

The predicted intent matched the expected intent, but the system predicted:

```text
auto_handle
```

while the expected decision was:

```text
escalate
```

The retrieval similarity was:

```text
1.0
```

This demonstrates that similarity alone is not a sufficient safety signal.

### Hypothesis

The decision layer needs stronger detection for complaints, sensitive situations, and unresolved customer frustration.

---

## Failure 2 — Payment issues can require investigation

Example:

```text
haven't got the cashback for the 1st Recharge via Amazon pay,
it's being 15 days now
```

The system predicted:

```text
payment_issue
auto_handle
```

while the expected decision was:

```text
escalate
```

with similarity:

```text
1.0
```

### Hypothesis

A high similarity score should not override signals such as delayed cashback, missing funds, or account-specific financial investigation.

---

## Failure 3 — Ambiguous delivery/order/product boundaries

Several reviewed examples show that messages can contain multiple support concepts.

For example, a customer may mention:

* an order
* a delivery delay
* a missing item
* a refund
* a damaged product

in the same message.

This makes single-label intent classification difficult.

### Hypothesis

A future system should allow hierarchical or multi-label intent detection before selecting a final support category.

---

## Failure 4 — Service complaints can resemble ordinary requests

Some customer messages contain short statements with little explicit intent but strong dissatisfaction.

Examples include:

```text
But can not understand the cause of delay
```

or messages expressing repeated contact or dissatisfaction.

The current system uses explicit complaint signals such as:

```text
no answer
no response
again
already contacted
complaint
shameful
ridiculous
terrible
worst
```

to identify escalation cases.

### Hypothesis

A more robust approach should model customer sentiment, repetition, unresolved status, and requested action instead of relying primarily on keyword signals.

---

## Failure 5 — Historical responses can contain hidden assumptions

Historical AmazonHelp responses may refer to:

* account information
* order information
* external support links
* specific customer context
* previous conversations

The current system cleans historical responses before presenting them, including removing usernames and URLs.

However, removing these elements does not guarantee that every remaining response is appropriate for a new customer.

### Hypothesis

A future response-generation layer should explicitly verify that every statement in the response is supported by the current customer message and retrieved evidence.

---

# 18. Auto-handle Safety Policy

The current policy uses retrieval similarity together with intent-specific signals.

For example, delivery-related signals can force escalation when the message indicates a potentially unresolved or incorrect delivery situation.

Prime-related billing, refund, cancellation, renewal, and problem signals can also trigger escalation.

Product issues containing signals such as:

```text
refund
charged
wrong
missing
damaged
broken
cancel
urgent
call me
not working
complaint
customer service
```

are treated conservatively.

The general fallback is:

```text
similarity >= 0.70
        ↓
auto_handle

otherwise
        ↓
escalate
```

The important limitation is that this threshold is a prototype heuristic, not a production-calibrated safety threshold.

---

# 19. Reproducibility

## Clone the repository

```powershell
git clone https://github.com/SWETHA8685/customer_support_ai.git
cd customer_support_ai
```

## Create the virtual environment

```powershell
py -3.13 -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

## Install dependencies

If `requirements.txt` is present:

```powershell
pip install -r requirements.txt
```

If the raw dataset is required, download the TWCS dataset separately and place:

```text
data/raw/twcs.csv
```

The large raw dataset is intentionally excluded from Git.

---

# 20. Running the Agent

Run the command-line agent:

```powershell
python src\agent.py
```

The agent accepts customer messages and returns:

```text
intent
decision
suggested_response
reason
evidence
```

The evidence includes the retrieved historical customer message, historical response, similarity score, and historical intent.

---

# 21. Running the GUI

The project also contains a simple desktop GUI.

Run:

```powershell
python src\gui.py
```

The interface allows a customer message to be entered and analyzed.

The result displays:

* Predicted intent
* Handling decision
* Evidence
* Suggested response

---

# 22. Evaluation Commands

Run the main evaluation:

```powershell
python evaluation\evaluate_agent.py
```

The results are written to:

```text
evaluation/evaluation_results.csv
```

Run decision analysis:

```powershell
python evaluation\analyze_decisions.py
```

Run the trivial/simple baselines:

```powershell
python evaluation\evaluate_baselines.py
python evaluation\evaluate_simple_baseline.py
```

Run the LLM response-quality evaluation:

```powershell
python evaluation\evaluate_llm_judge.py
```

---

# 23. Project Structure

```text
customer_support_ai/
│
├── data/
│   └── golden/
│       ├── sample_200.csv
│       ├── golden_set.csv
│       ├── golden_set_final.csv
│       ├── golden_set_reviewed.csv
│       └── delivery_not_received_candidates.csv
│
├── evaluation/
│   ├── LABELING_RUBRIC.md
│   ├── LLM_JUDGE_RUBRIC.md
│   ├── analyze_decisions.py
│   ├── analyze_results.py
│   ├── baselines.py
│   ├── decision_metrics.py
│   ├── evaluate_agent.py
│   ├── evaluate_baselines.py
│   ├── evaluate_llm_judge.py
│   ├── evaluate_simple_baseline.py
│   ├── evaluation_results.csv
│   ├── simple_baseline_results.csv
│   └── trivial_baseline_results.csv
│
├── src/
│   ├── agent.py
│   ├── classifier.py
│   ├── discover_intents.py
│   ├── gui.py
│   ├── label_golden.py
│   ├── prepare_training.py
│   ├── prepare_training_v2.py
│   └── retriever.py
│
├── .gitignore
└── README.md
```

Large raw and processed datasets are excluded from Git through `.gitignore`.

---

# 24. Decision Log

The following are the main non-obvious design decisions made during development.

1. **Focused on AmazonHelp rather than the complete TWCS dataset**
   This reduced the scope enough to build and evaluate a complete support workflow.

2. **Used intent classification before retrieval**
   Retrieval is restricted to relevant support categories to reduce unrelated historical matches.

3. **Used historical conversations as response evidence**
   This provides grounding in actual support behavior.

4. **Separated classification from automation decision**
   Knowing what the customer wants is different from knowing whether automation is safe.

5. **Added an escalation path**
   Cases without adequate evidence should reach a human rather than receive an unsupported answer.

6. **Used a retrieval similarity threshold**
   The threshold provides a simple initial confidence mechanism.

7. **Added intent-specific safety signals**
   Delivery, payment, Prime, product, and service-complaint cases can require different handling.

8. **Removed golden examples from retrieval during evaluation**
   This reduces direct evaluation leakage.

9. **Cleaned historical responses before presenting them**
   Twitter usernames, URLs, and unnecessary whitespace are removed.

10. **Kept the original historical response as evidence**
    This makes the system more inspectable.

11. **Used a small manually reviewed golden set**
    This allowed focused manual quality control instead of attempting to label millions of tweets.

12. **Evaluated decision quality separately from intent quality**
    Automation errors have different consequences from classification errors.

13. **Included failure analysis rather than reporting only accuracy**
    Aggregate accuracy does not reveal all operational risks.

14. **Kept the system as a prototype**
    No real account, payment, refund, or order actions are performed.

15. **Excluded the large raw dataset from GitHub**
    This keeps the repository practical to clone and review.

---

# 25. What I Would Do With One More Week

With one additional week, I would prioritize the following:

### 1. Improve the auto-handle policy

Replace the mostly heuristic decision layer with a calibrated classifier using:

* retrieval similarity
* intent
* customer sentiment
* unresolved/repeated-contact signals
* requested action
* risk category
* evidence quality

### 2. Improve golden-set coverage

Increase the reviewed evaluation set and deliberately sample:

* ambiguous cases
* multilingual cases
* payment cases
* refund cases
* delivery failures
* repeated complaints
* sensitive cases
* low-context messages

### 3. Improve response generation

Instead of directly reusing a historical response, generate a response from structured evidence while requiring every important claim to be supported by the retrieved context.

### 4. Add stronger leakage checks

Check for:

* duplicate customer messages
* near-duplicate conversations
* temporal leakage
* overlapping conversation threads

### 5. Calibrate automation thresholds

Rather than selecting `0.70` only as a heuristic threshold, choose thresholds using a validation set and explicitly optimize the trade-off between:

```text
safe automation
vs.
unnecessary escalation
```

### 6. Improve human evaluation

Run a blinded human review of a sample of responses and compare human judgments with the automated quality judge.

---

# 26. Limitations

This prototype has several important limitations:

* Evaluation is based on a relatively small manually reviewed set.
* Class distribution is not uniform.
* Historical support responses may depend on context unavailable to the model.
* Retrieval similarity does not guarantee resolution correctness.
* Keyword-based safety signals can miss new forms of risky language.
* LLM-based response evaluation can vary.
* The system does not have access to real customer accounts or orders.
* The system does not perform real refunds, cancellations, or payments.
* The raw TWCS dataset is not included in the repository.
* The current decision threshold is heuristic rather than production-calibrated.

---

# 27. Example

Input:

```text
My package has not arrived yet
```

Possible pipeline:

```text
Intent:
delivery_not_received

        ↓

Historical retrieval:
similar AmazonHelp delivery cases

        ↓

Safety decision:
auto_handle OR escalate

        ↓

Suggested response:
grounded in the retrieved historical support response
```

Another example:

```text
I have contacted support three times and nobody has helped me.
```

The system should recognize the repeated/unresolved support signal and favor escalation rather than relying only on retrieval similarity.

---

# 28. Evidence and Interpretability

For every analyzed message, the agent attempts to return:

```text
Intent
Decision
Reason
Suggested Response
Historical Evidence
Similarity
Historical Intent
```

This makes the output inspectable rather than presenting only a final answer.

The implementation explicitly returns the retrieved historical customer message, historical response, similarity score, and historical intent as evidence.

---

# 29. Repository

GitHub repository:

**SWETHA8685/customer_support_ai**

The repository contains the source code, evaluation scripts, golden-set artifacts, rubrics, and documented evaluation outputs.

---

# 30. Author

**Swetha T.**

Hiver SDE Intern Take-Home Assignment
