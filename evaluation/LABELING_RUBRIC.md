# Golden Set Labeling Rubric

## Purpose

The golden set contains 200 AmazonHelp customer-support examples.
Each example is manually reviewed for intent and handling decision.

## Intent labels

### delivery_issue
Problems with delivery timing, delays, tracking, shipping, or courier delivery.

### delivery_not_received
The order is explicitly marked delivered/handed over, but the customer says they did not receive it.

### order_issue
Problems with an order itself, including cancellation, modification, wrong order, or order status.

### refund_return
Requests or problems involving refunds, returns, reimbursements, or money being returned after a return.

### payment_issue
Payment, billing, charge, transaction, Amazon Pay, card, or unexpected payment problems.

### prime_membership
Amazon Prime membership, subscription, Prime benefits, or Prime-specific problems.

### account_issue
Login, account access, account settings, or account-specific access problems.

### product_issue
Problems/questions about a specific product, product availability, product functionality, damage, or product characteristics.

### service_complaint
General dissatisfaction with Amazon support/service when no more specific intent clearly applies.

## Handling decision

### auto_handle

Use auto_handle when:

- The request is routine or informational.
- The customer is asking a straightforward question.
- The issue can reasonably be answered from historical support examples.
- There is no clear unresolved escalation signal.
- No sensitive account/payment intervention is required.

### escalate

Use escalate when:

- The customer explicitly requests a human/support representative.
- The customer reports repeated failed attempts to get help.
- The customer says the issue remains unresolved after previous contact.
- There is significant payment/account risk.
- The historical evidence is insufficient to safely answer the request.
- The customer reports a situation requiring investigation or case-specific intervention.

## Important labeling rules

1. Choose the most specific intent available.
2. Do not use service_complaint when a more specific intent clearly describes the problem.
3. "Delivered but not received" is delivery_not_received, not delivery_issue.
4. Emotional language alone does not automatically require escalation.
5. Repeated unsuccessful support/contact is a strong escalation signal.
6. Explicit requests for contact or human support should normally escalate.
7. When intent is ambiguous, choose the best-supported label and record the ambiguity in the decision log/report.