import re

from classifier import IntentClassifier
from retriever import HistoricalResponseRetriever


class SupportAgent:
    def __init__(self):
        print("Initializing Support Agent...")

        self.classifier = IntentClassifier()
        self.retriever = HistoricalResponseRetriever()
        print("Support Agent ready.")

    # =========================================================
    # DECISION POLICY
    # =========================================================

    def decide_escalation(self, intent, message, similarity):
        """
        Decide whether a customer message should be:

        auto_handle
        or
        escalate

        The policy is intentionally conservative because this is
        a customer-support setting where an unsafe automatic reply
        is more serious than an unnecessary escalation.
        """

        message_lower = message.lower()

        # =====================================================
        # HIGH-RISK INTENTS
        # =====================================================

        # Account, payment and refund cases are always escalated
        # because they can involve sensitive account or financial
        # consequences.

        high_risk_intents = {
            "account_issue",
            "payment_issue",
            "refund_return",
        }

        if intent in high_risk_intents:
            return (
                "escalate",
                "This intent involves a high-risk account, payment, "
                "or refund issue and should be reviewed by a human."
            )

        # =====================================================
        # DELIVERY NOT RECEIVED
        # =====================================================

        if intent == "delivery_not_received":

            unresolved_signals = [
                "no response",
                "no answer",
                "no answers",
                "call me",
                "no call",
                "no calls",
                "did not receive",
                "didn't receive",
                "didnt receive",
                "still",
                "urgent",
                "week",
                "weeks",
                "month",
                "months",
                "already contacted",
                "contacted",
                "complaint",
                "helpless",
            ]

            if any(
                signal in message_lower
                for signal in unresolved_signals
            ):
                return (
                    "escalate",
                    "The customer indicates an unresolved or repeated "
                    "delivery problem that requires human support."
                )

            if similarity >= 0.70:
                return (
                    "auto_handle",
                    "Strong historical evidence supports an automated "
                    "delivery response."
                )

            return (
                "escalate",
                "There is not enough historical evidence to safely "
                "draft the response."
            )

        # =====================================================
        # ORDER ISSUE
        # =====================================================

        if intent == "order_issue":

            order_signals = [

                # Order identification
                "order no",
                "order number",
                "order #",

                # Cancellation
                "cancel",
                "cancelled",
                "canceled",

                # Order modification
                "changed",
                "change order",
                "modify order",

                # Repeated/unresolved order issue
                "still",
                "already",

                # Missing item/order
                "not received",
                "missing",
                "missing item",

                # Wrong item/product
                "wrong order",
                "wrong item",
                "wrong product",
                "received wrong",

                # Refund
                "refund",

                # Replacement/corrective request
                "replacement",
                "send me",
                "send it",
                "send my",

                # Urgent request
                "asap",

                # Explicitly referring to something ordered
                "ordered",
            ]

            if any(
                signal in message_lower
                for signal in order_signals
            ):
                return (
                    "escalate",
                    "The message contains an order-specific problem "
                    "or corrective request that should be reviewed "
                    "by a human."
                )

            # Order issues require stronger retrieval evidence
            # than generic support complaints.
            if similarity >= 0.80:
                return (
                    "auto_handle",
                    "Strong historical evidence supports an automated "
                    "response."
                )

            return (
                "escalate",
                "There is not enough historical evidence to safely "
                "draft the response."
            )

        # =====================================================
        # DELIVERY ISSUE
        # =====================================================

        if intent == "delivery_issue":

            delivery_signals = [

                # Urgency
                "urgent",
                "call me",

                # Important delivery state
                "out for delivery",

                # Repeated/unresolved
                "still",
                "already",

                # Not received
                "not received",
                "never received",
                "didn't receive",
                "didnt receive",
                "haven't received",
                "havent received",

                # Missing package
                "missing",

                # No support
                "nobody",
                "no one",
                "no response",
                "no answer",
                "no answers",

                # Long delay
                "week",
                "weeks",
                "month",
                "months",

                # Cancellation
                "cancel",

                # Incorrect destination
                "wrong address",
                "wrong location",
                "wrong place",
                "sent to",
                "shipped to",
                "delivered to",

                # Support complaint
                "customer care",
                "customer service",
                "helpless",
                "complaint",

                # Incorrect delivery
                "wrong delivery",
                "wrong destination",
            ]

            if any(
                signal in message_lower
                for signal in delivery_signals
            ):
                return (
                    "escalate",
                    "The message indicates a potentially unresolved "
                    "or incorrect delivery situation."
                )

            if similarity >= 0.70:
                return (
                    "auto_handle",
                    "Strong historical evidence supports an automated "
                    "response."
                )

            return (
                "escalate",
                "There is not enough historical evidence to safely "
                "draft the response."
            )

        # =====================================================
        # SERVICE COMPLAINT
        # =====================================================

        if intent == "service_complaint":

            complaint_signals = [

                # Lack of support
                "helpless",
                "no answers",
                "no answer",
                "no response",
                "nobody",
                "no one",

                # Repeated contact
                "third time",
                "fourth time",
                "fifth time",
                "again",
                "already contacted",
                "contacted before",

                # Explicit complaint
                "complaint",
                "responsibility",

                # Strong negative language
                "shameful",
                "ridiculous",
                "terrible",
                "worst",
            ]

            if any(
                signal in message_lower
                for signal in complaint_signals
            ):
                return (
                    "escalate",
                    "The customer expresses a repeated or unresolved "
                    "service complaint that should be reviewed by a human."
                )

            if similarity >= 0.70:
                return (
                    "auto_handle",
                    "Strong historical evidence supports an automated "
                    "response."
                )

            return (
                "escalate",
                "There is not enough historical evidence to safely "
                "draft the response."
            )

        # =====================================================
        # PRIME MEMBERSHIP
        # =====================================================

        if intent == "prime_membership":

            prime_signals = [

                # Billing
                "charged",
                "charge",
                "wrong charge",

                # Refund
                "refund",

                # Cancellation
                "cancel",
                "cancelled",
                "canceled",

                # Renewal
                "renewed",
                "renewal",

                # Problems
                "problem",
                "issue",
                "not working",
                "cannot",
                "can't",
            ]

            if any(
                signal in message_lower
                for signal in prime_signals
            ):
                return (
                    "escalate",
                    "The Prime membership message involves a billing, "
                    "cancellation, or service problem."
                )

            if similarity >= 0.70:
                return (
                    "auto_handle",
                    "Strong historical evidence supports an automated "
                    "response."
                )

            return (
                "escalate",
                "There is not enough historical evidence to safely "
                "draft the response."
            )

        # =====================================================
        # PRODUCT ISSUE
        # =====================================================

        if intent == "product_issue":

            product_signals = [

                # Financial/corrective issues
                "refund",
                "charged",

                # Wrong/missing/damaged
                "wrong",
                "missing",
                "damaged",
                "broken",

                # Cancellation
                "cancel",
                "cancelled",
                "canceled",

                # Urgency
                "urgent",
                "call me",

                # Product malfunction
                "not working",
                "doesn't work",
                "doesnt work",

                # Complaint/support
                "complaint",
                "customer service",
                "customer care",
                "helpless",
                "no answer",
                "no response",
            ]

            if any(
                signal in message_lower
                for signal in product_signals
            ):
                return (
                    "escalate",
                    "The product issue may require corrective action "
                    "or human support."
                )

            if similarity >= 0.70:
                return (
                    "auto_handle",
                    "Strong historical evidence supports an automated "
                    "response."
                )

            return (
                "escalate",
                "There is not enough historical evidence to safely "
                "draft the response."
            )

        # =====================================================
        # DEFAULT POLICY
        # =====================================================

        if similarity >= 0.70:
            return (
                "auto_handle",
                "Strong historical evidence supports an automated "
                "response."
            )

        return (
            "escalate",
            "There is not enough historical evidence to safely "
            "draft the response."
        )

    # =========================================================
    # RESPONSE CLEANING
    # =========================================================

    def clean_response(self, response):
        """
        Clean a historical response before using it as a
        suggested response.

        Removes:
        - Twitter usernames
        - URLs
        - unnecessary whitespace
        """

        if not response:
            return response

        # Remove Twitter usernames
        response = re.sub(
            r"@\w+",
            "",
            response
        )

        # Remove URLs
        response = re.sub(
            r"https?://\S+",
            "",
            response
        )

        # Normalize whitespace
        response = re.sub(
            r"\s+",
            " ",
            response
        ).strip()

        return response

    # =========================================================
    # MAIN AGENT HANDLER
    # =========================================================

    def handle(self, message):
        """
        Complete support-agent pipeline:

        Customer message
                ↓
        Intent classification
                ↓
        Historical retrieval
                ↓
        Safety decision
                ↓
        Suggested response
        """

        # -----------------------------------------------------
        # STEP 1: INTENT
        # -----------------------------------------------------

        intent = self.classifier.predict(
            message
        )

        # -----------------------------------------------------
        # STEP 2: RETRIEVE SIMILAR CASES
        # -----------------------------------------------------

        historical_cases = self.retriever.retrieve(
            message,
            intent=intent,
            top_k=3
        )

        # -----------------------------------------------------
        # NO HISTORICAL EVIDENCE
        # -----------------------------------------------------

        if not historical_cases:

            return {
                "intent": intent,

                "decision": "escalate",

                "suggested_response": (
                    "This case should be reviewed by a human "
                    "support agent."
                ),

                "reason": (
                    "No sufficiently similar historical conversation "
                    "was found."
                ),

                "evidence": None,
            }

        # -----------------------------------------------------
        # BEST MATCH
        # -----------------------------------------------------

        best_case = historical_cases[0]

        similarity = float(
            best_case.get(
                "similarity",
                0.0
            )
        )

        # -----------------------------------------------------
        # STEP 3: SAFETY DECISION
        # -----------------------------------------------------

        decision, reason = self.decide_escalation(
            intent,
            message,
            similarity
        )

        # -----------------------------------------------------
        # STEP 4: RESPONSE
        # -----------------------------------------------------

        if decision == "auto_handle":

            historical_response = best_case.get(
                "agent_response",
                ""
            )

            suggested_response = self.clean_response(
                historical_response
            )

            # Fallback if historical response is empty
            if not suggested_response:

                suggested_response = (
                    "Thanks for contacting Amazon. "
                    "We are happy to help with your request."
                )

        else:

            suggested_response = (
                "This case should be reviewed by a human "
                "support agent."
            )

        # -----------------------------------------------------
        # STEP 5: RESULT
        # -----------------------------------------------------

        return {

            "intent": intent,

            "decision": decision,

            "suggested_response": suggested_response,

            "reason": reason,

            "evidence": {

                "customer_message":
                    best_case.get(
                        "customer_message",
                        ""
                    ),

                "historical_response":
                    best_case.get(
                        "agent_response",
                        ""
                    ),

                "similarity":
                    similarity,

                "intent":
                    best_case.get(
                        "intent",
                        intent
                    ),
            },
        }


# =============================================================
# MANUAL TEST
# =============================================================

if __name__ == "__main__":

    agent = SupportAgent()

    test_messages = [

        "My package has not arrived yet",

        "I need a refund for my order",

        "My Amazon Pay payment failed",

        "I cannot login to my account",

        "I want to cancel my order",

        "How much does Amazon Prime cost?",

        # Previously unsafe order case
        (
            "@AmazonHelp @115850 trimmer and bedsheet means the same! "
            "I can keep the bedsheet if it's a Diwali gift but send "
            "me the trimmer I had ordered ASAP."
        ),

        # Previously unsafe delivery case
        "@AmazonHelp It says out for delivery",

        # Previously unsafe delivery-not-received case
        "@AmazonHelp Still I did not receive any calls from Amazon",
    ]

    print("\n")
    print("=" * 70)
    print("SUPPORT AGENT TEST")
    print("=" * 70)

    for message in test_messages:

        print("\nCustomer:")
        print(message)

        result = agent.handle(
            message
        )

        print("\nIntent:")
        print(result["intent"])

        print("\nDecision:")
        print(result["decision"])

        print("\nReason:")
        print(result["reason"])

        if result["evidence"]:

            print("\nSimilarity:")
            print(
                f"{result['evidence']['similarity']:.3f}"
            )

        print("\nSuggested Response:")
        print(
            result["suggested_response"]
        )

        print("\n" + "-" * 70)