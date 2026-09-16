# AI Customer Support Agent

An AI-assisted customer support agent built using the **Customer Support on Twitter (TWCS)** dataset. The system focuses on **AmazonHelp** conversations and demonstrates intent classification, grounded response drafting, and automated handling/escalation decisions.

## Overview

The system processes customer-support conversations and performs the following workflow:

```text
Customer Message
       ↓
Intent Classification
       ↓
Response Drafting
       ↓
Handling Decision
       ↓
Auto-handle / Escalate
```

The project was developed as part of the Hiver SDE take-home assignment.

## Key Features

* AmazonHelp customer-support conversation extraction
* Customer intent classification
* Grounded customer-response drafting
* Auto-handle vs. escalation decision
* Golden dataset for validation
* Automated evaluation metrics
* LLM-based response quality checks
* Decision logging
* Simple Python GUI for testing the support-agent workflow

## Supported Intents

The classifier currently identifies the following customer intents:

* `account_issue`
* `delivery_issue`
* `delivery_not_received`
* `order_issue`
* `payment_issue`
* `prime_membership`
* `product_issue`
* `refund_return`
* `service_complaint`

## Dataset

This project uses the **Customer Support on Twitter (TWCS)** dataset.

The original dataset contains Twitter customer-support conversations involving brands and their customers. For this project, the analysis focuses on the **AmazonHelp** account.

### Data Processing

The raw dataset is processed to extract customer-agent conversation pairs with fields including:

```text
customer_tweet_id
customer_id
customer_message
customer_created_at
agent_tweet_id
agent_response
```

The full raw dataset is intentionally **not included in this repository** because of its large file size.
## Project Structure

```text
hiver-sde-assignment/
│
├── data/
│   ├── golden/
│   │   └── sample_200.csv
│   │
│   ├── processed/
│   │   └── generated processing outputs
│   │
│   └── raw/
│       └── TWCS dataset
│
├── evaluation/
│   ├── evaluation scripts
│   ├── reports
│   └── decision logs
│
├── src/
│   ├── classifier.py
│   ├── gui.py
│   └── other source modules
│
├── tests/
│   └── test files
│
├── .gitignore
└── README.md
```

## Requirements

* Python 3.13+
* pip
* Git
* Windows/macOS/Linux

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/SWETHA8685/customer.git
cd customer
```

### 2. Create a virtual environment

Windows:

```powershell
py -3.13 -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## Dataset Setup

Download the Customer Support on Twitter dataset separately and place the required raw CSV at:

```text
data/raw/twcs.csv
```

The raw dataset is excluded from Git using `.gitignore` because of its large size.

After placing the dataset in the expected location, run the project's data-processing scripts to generate the AmazonHelp conversation data.

## Running the Classifier

From the project root:

```powershell
python src\classifier.py
```

The classifier processes the available customer-support examples and displays the intent classification results.

## Running the GUI

Run:

```powershell
python src\gui.py
```

The GUI provides an interactive interface for testing the customer-support workflow.

## Support Workflow

The support agent handles customer conversations through the following stages:

### 1. Intent Classification

The customer's message is analyzed and assigned to one of the supported intents.

### 2. Response Drafting

A response is drafted based on the available customer-support context.

### 3. Handling Decision

The system determines whether the conversation can be handled automatically or should be escalated.

### Auto-handle

Used when the request can be safely answered using the available information and does not require sensitive or human-only intervention.

### Escalate

Used when the request requires human support, additional verification, or circumstances where automatically responding could be inappropriate.

The handling decision is recorded in the project decision logs.

## Reproducibility

The repository contains the source code and supporting artifacts required to understand and reproduce the implemented workflow.

Because the original TWCS dataset is large, it is not stored in GitHub. The dataset should be downloaded separately before running the complete data-processing pipeline.

## Limitations

* The current classifier can misclassify ambiguous customer messages.
* Intent categories can overlap, particularly between delivery, order, and product-related issues.
* Response generation quality depends on the available conversation context.
* LLM-based quality checks can introduce evaluator variability.
* The complete raw dataset is excluded from the repository because of its size.

## Future Improvements

Potential improvements include:

* Fine-tuning a stronger intent-classification model
* Better conversation-thread reconstruction
* Retrieval-augmented response generation
* More comprehensive escalation rules
* Confidence-based human handoff
* Improved response-grounding checks
* Larger and more systematically reviewed datasets
* Additional automated safety and quality checks

## Author

**Swetha T.**
