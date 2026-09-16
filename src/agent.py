
import re

from classifier import IntentClassifier
from retriever import HistoricalResponseRetriever


class SupportAgent:
    def __init__(self):
        print("Initializing support agent...")
        self.classifier = IntentClassifier()
        self.retriever = HistoricalResponseRetriever()

    def normalize_text(self, text):
        text = str(text).lower().strip()

        # Remove quotation marks and backslashes
        text = re.sub(r'[“”"\'\\]', '', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        return text

    def decide(self, customer_message, intent, similarity):
        text = self.normalize_text(customer_message)

        # =====================================================
        # GLOBAL SAFETY OVERRIDES
        # =====================================================

        # -----------------------------------------------------
        # 1. EXISTING CASE / UPDATE REQUEST
        # -----------------------------------------------------
        explicit_update_signals = [
            "any update",
            "any updates",
            "any update on this",
            "any updates on this",
            "whats the update",
            "what is the update",
            "whats the latest",
            "what is the latest",
            "status update",
            "any news",
        ]

        if any(signal in text for signal in explicit_update_signals):
            return (
                "escalate",
                "The customer is requesting an update on an existing case, which may require case-specific information.",
            )

        # -----------------------------------------------------
        # 2. SCAM / PHISHING / IMPERSONATION
        # -----------------------------------------------------
        scam_signals = [
            "scam",
            "scams",
            "phishing",
            "fraud",
            "fraudulent",
            "fake amazon",
            "not amazon",
            "pretending to be amazon",
            "amazonちゃう",
            "amazonちゃうよな",
        ]

        if any(signal in text for signal in scam_signals):
            return (
                "escalate",
                "The message raises a potential scam, fraud, or impersonation concern that requires human review.",
            )

        # -----------------------------------------------------
        # 3. INSUFFICIENT-CONTEXT SELLER / FULFILLMENT INFO
        # -----------------------------------------------------
        #
        # These messages may be part of a delivery problem but
        # contain seller/fulfillment information without enough
        # customer context to safely resolve the issue.
        #
        # This rule intentionally supports multiple languages
        # and wording variations.
        # -----------------------------------------------------
        insufficient_context_signals = [
            # English
            "managed by amazon",
            "sold by amazon",
            "sold by amazon eu",
            "managed by amazon.",
            "sold by amazon.",

            # Spanish
            "gestionado por amazon",
            "gestionada por amazon",
            "vendido por amazon",
            "vendida por amazon",
            "vendido por amazon eu",
            "vendida por amazon eu",
            "gestionado por amazon vendido por",
            "gestionada por amazon vendida por",

            # Common Amazon seller/company references
            "amazon eu s.a.r.l",
            "amazon eu sarl",
        ]

        if any(signal in text for signal in insufficient_context_signals):
            return (
                "escalate",
                "The message provides seller or fulfillment information but insufficient customer context to safely determine the requested resolution.",
            )

        # -----------------------------------------------------
        # 4. URL-ONLY / ALMOST URL-ONLY MESSAGE
        # -----------------------------------------------------
        if "http" in text:
            text_without_urls = re.sub(
                r'https?://\S+',
                '',
                text
            ).strip()

            if len(text_without_urls) < 12:
                return (
                    "escalate",
                    "The message contains insufficient context for a safe automatic response.",
                )

        # =====================================================
        # ACCOUNT / CONTACT / LOGIN SAFETY
        # =====================================================

        account_signals = [
            "mobile number",
            "phone number",
            "phone",
            "mobile",
            "account",
            "login",
            "log in",
            "sign in",
            "signin",
            "password",
            "email address",
            "email id",
            "change my number",
            "change number",
            "update my number",
            "update phone",
            "update mobile",
        ]

        if any(signal in text for signal in account_signals):
            return (
                "escalate",
                "The message involves an account or contact-detail issue that may require account-specific verification or human intervention.",
            )

        # =====================================================
        # EXPLICIT UNRESOLVED SUPPORT
        # =====================================================

        explicit_unresolved_signals = [
            "shared the required details",
            "shared the details",
            "provided the required details",
            "provided the details",
            "resolve the issue asap",
            "resolve this issue asap",
            "resolve the issue",
            "resolve this issue",
            "please resolve",
            "please fix this",
            "it just disappears",
            "it just disappear",
            "no. it just disappears",
            "no it just disappears",
            "no. it just disappear",
            "no it just disappear",
            "it just diappears",
            "no. it just diappears",
            "no it just diappears",

            # Repeated support / failed previous attempts
            "raised it before",
            "no one does anything",
            "no one is doing anything",
            "done that",
            "have done that",
            "already raised",
            "already complained",
            "already contacted",
            "already contacted amazon",
            "still no response",
            "no response",
            "not getting any response",
            "not getting any email response",
            "fifth time",
            "9th time",
            "ninth time",
            "again and again",
            "multiple times",
            "several times",
        ]

        if any(signal in text for signal in explicit_unresolved_signals):
            return (
                "escalate",
                "The customer indicates an unresolved issue, repeated unsuccessful support, or insufficient context for safe automatic handling.",
            )

        # =====================================================
        # EXPLICIT HUMAN / INVESTIGATION REQUEST
        # =====================================================

        human_request_signals = [
            "call me",
            "call us",
            "speak to me",
            "speak with me",
            "human",
            "real person",
            "representative",
            "agent",
            "customer service",
            "customer support",
            "contact me",
            "someone help",
            "need help",
            "help me",
            "please investigate",
            "investigate this",
            "look into this",
            "look into it",
            "supervisor",
        ]

        if any(signal in text for signal in human_request_signals):
            return (
                "escalate",
                "The customer explicitly requests human assistance or case-specific intervention.",
            )

        # =====================================================
        # PAYMENT
        # =====================================================

        if intent == "payment_issue":
            return (
                "escalate",
                "Payment-related issues can involve financial information or account-specific transactions and therefore require human review.",
            )

        # =====================================================
        # ACCOUNT
        # =====================================================

        if intent == "account_issue":
            return (
                "escalate",
                "Account-related issues may require account-specific verification or intervention.",
            )

        # =====================================================
        # REFUND / RETURN
        # =====================================================

        if intent == "refund_return":

            refund_escalation_signals = [
                "refund pending",
                "refund missing",
                "refund not received",
                "still waiting",
                "not received my refund",
                "where is my refund",
                "refund hasn't",
                "refund hasnt",
                "refund did not",
                "refund didn't",
                "return not",
                "return failed",
                "return cancelled",
                "return canceled",
                "cancel my return",
                "urgent",
                "asap",
            ]

            if any(
                signal in text
                for signal in refund_escalation_signals
            ):
                return (
                    "escalate",
                    "The refund or return appears unresolved or case-specific and requires human intervention.",
                )

            return (
                "escalate",
                "Refund and return requests can involve order-specific actions, so they are escalated for safe handling.",
            )

        # =====================================================
        # DELIVERY NOT RECEIVED
        # =====================================================

        if intent == "delivery_not_received":

            delivered_signals = [
                "delivered",
                "marked delivered",
                "shows delivered",
                "says delivered",
                "delivery notification",
                "delivery notification says",
                "notification says",
                "handed",
                "left at",
                "left outside",
                "left unattended",
            ]

            not_received_signals = [
                "not received",
                "didn't receive",
                "did not receive",
                "never received",
                "haven't received",
                "havent received",
                "not got",
                "didn't get",
                "did not get",
                "never got",
                "missing package",
                "missing parcel",
                "where is my package",
                "where is my parcel",
                "can't find",
                "cannot find",
                "lost package",
                "lost parcel",
                "isn't in my mailbox",
                "is not in my mailbox",
                "isnt in my mailbox",
                "isn't in my",
                "is not in my",
                "isnt in my",
            ]

            # -------------------------------------------------
            # UNRESOLVED MISSING DELIVERY / CONTACT
            # -------------------------------------------------

            unresolved_missing_delivery_signals = [
                "still did not receive",
                "still didn't receive",
                "still havent received",
                "still haven't received",
                "still did not get",
                "still didn't get",
                "still not received",
                "still not got",
                "did not receive any calls",
                "didn't receive any calls",
                "did not get any calls",
                "didn't get any calls",
                "nobody called",
                "no one called",
                "no calls from amazon",
                "no call from amazon",
            ]

            if any(
                signal in text
                for signal in unresolved_missing_delivery_signals
            ):
                return (
                    "escalate",
                    "The customer reports that the delivery issue remains unresolved, including a missing expected contact or delivery follow-up.",
                )

            # -------------------------------------------------
            # DELIVERED BUT NOT RECEIVED
            # -------------------------------------------------

            if (
                any(
                    signal in text
                    for signal in delivered_signals
                )
                and any(
                    signal in text
                    for signal in not_received_signals
                )
            ):
                return (
                    "escalate",
                    "The order is marked as delivered but the customer reports not receiving it, which requires delivery investigation.",
                )

            # -------------------------------------------------
            # CUSTOMER CHECKED LOCATIONS / NEIGHBORS
            # -------------------------------------------------

            checked_for_missing_package = [
                "looked all around",
                "looked everywhere",
                "checked everywhere",
                "checked all around",
                "checked my mailbox",
                "checked the mailbox",
                "asked my neighbors",
                "asked neighbors",
                "checked with my neighbors",
                "neighbors and nobody",
                "nobody has it",
                "no one has it",
            ]

            if (
                any(
                    signal in text
                    for signal in not_received_signals
                )
                and any(
                    signal in text
                    for signal in checked_for_missing_package
                )
            ):
                return (
                    "escalate",
                    "The customer reports a missing delivery after checking likely delivery locations or nearby recipients, requiring investigation.",
                )

            # -------------------------------------------------
            # GENERAL UNRESOLVED MISSING DELIVERY
            # -------------------------------------------------

            if (
                any(
                    signal in text
                    for signal in not_received_signals
                )
                and any(
                    signal in text
                    for signal in [
                        "urgent",
                        "asap",
                        "no one",
                        "nobody",
                        "still waiting",
                        "not helping",
                        "help me",
                    ]
                )
            ):
                return (
                    "escalate",
                    "The customer reports an unresolved missing-delivery issue requiring investigation.",
                )

            if similarity >= 0.40:
                return (
                    "auto_handle",
                    "The message is sufficiently similar to historical delivery-resolution conversations and does not contain a strong escalation signal.",
                )

            return (
                "escalate",
                "There is insufficient historical evidence for safe automatic handling of the delivery issue.",
            )

        # =====================================================
        # ORDER
        # =====================================================

        if intent == "order_issue":

            order_case_signals = [
                "order cancelled",
                "order canceled",
                "wrong item",
                "wrong product",
                "duplicate order",
                "missing item",
                "items missing",
                "can't cancel",
                "cannot cancel",
                "unable to cancel",
                "cancel my order",
                "order not",
                "order was",
                "order has",
                "charged twice",
                "ordered twice",
                "only one delivered",
                "pre-order",
                "preorder",
                "out of stock",
                "substitute",
                "substituted",
                "urgent",
                "asap",
            ]

            if any(
                signal in text
                for signal in order_case_signals
            ):
                return (
                    "escalate",
                    "The message describes an order-specific problem that may require case-specific intervention.",
                )

            if similarity >= 0.80:
                return (
                    "auto_handle",
                    "The message is highly similar to historical order-support conversations and does not show a strong case-specific escalation signal.",
                )

            return (
                "escalate",
                "The historical evidence is not sufficiently strong for safe automatic handling of this order issue.",
            )

        # =====================================================
        # DELIVERY
        # =====================================================

        if intent == "delivery_issue":

            # -------------------------------------------------
            # OUT FOR DELIVERY SAFETY
            # -------------------------------------------------

            out_for_delivery_signals = [
                "out for delivery",
                "out-for-delivery",
            ]

            if any(
                signal in text
                for signal in out_for_delivery_signals
            ):
                return (
                    "escalate",
                    "The order is currently out for delivery and the available message does not provide enough context for safe automatic handling.",
                )

            delivery_unresolved_signals = [
                "late",
                "delayed",
                "delay",
                "missed delivery",
                "missed the delivery",
                "not delivered",
                "still waiting",
                "where is my delivery",
                "where is my package",
                "where is my parcel",
                "courier lied",
                "courier didn't",
                "courier did not",
                "left outside",
                "left unattended",
                "thrown",
                "damaged",
                "unsafe",
                "complaint",
                "guaranteed delivery",
                "guaranteed",
                "one day shipping",
                "one-day shipping",
                "delivery date",
                "cancel if",
                "cancel it",
                "nobody",
                "no one",
                "not helping",
                "urgent",
                "asap",
            ]

            simple_delivery_questions = [
                "what is my delivery date",
                "tell me delivery date",
                "when will it arrive",
                "when will my order arrive",
                "when will my package arrive",
                "when will my parcel arrive",
            ]

            if any(
                signal in text
                for signal in simple_delivery_questions
            ):
                if not any(
                    signal in text
                    for signal in [
                        "late",
                        "delayed",
                        "missed",
                        "not delivered",
                        "still waiting",
                        "complaint",
                    ]
                ):
                    if similarity >= 0.50:
                        return (
                            "auto_handle",
                            "The customer is requesting routine delivery information and the message is sufficiently similar to historical support conversations.",
                        )

            if any(
                signal in text
                for signal in delivery_unresolved_signals
            ):
                return (
                    "escalate",
                    "The delivery issue appears delayed, unresolved, unsafe, or case-specific and requires human intervention.",
                )

            if similarity >= 0.70:
                return (
                    "auto_handle",
                    "The message is sufficiently similar to historical delivery-support conversations and does not show a strong unresolved signal.",
                )

            return (
                "escalate",
                "There is insufficient historical evidence for safe automatic handling of the delivery issue.",
            )

        # =====================================================
        # SERVICE COMPLAINT
        # =====================================================

        if intent == "service_complaint":

            complaint_escalation_signals = [
                "complaint",
                "complain",
                "terrible service",
                "bad service",
                "poor service",
                "worst service",
                "rude",
                "rude representative",
                "unhelpful",
                "not helping",
                "not helpful",
                "no help",
                "nobody helped",
                "no one helped",
                "still not resolved",
                "not resolved",
                "issue remains",
                "problem remains",
                "still having",
                "still have the problem",
                "still having the problem",
                "frustrated",
                "fuming",
                "angry",
                "fed up",
                "done with",
                "never advise",
                "never recommend",
                "call me",
                "human",
                "representative",
                "customer service",
                "customer support",
                "resolve the issue",
                "resolve this issue",
                "please resolve",
                "please fix",
                "it just disappears",
                "it just disappear",
                "it just diappears",
                "no. it just disappears",
                "no it just disappears",
                "no. it just disappear",
                "no it just disappear",
                "no. it just diappears",
                "no it just diappears",

                # Repeated unsuccessful support
                "raised it before",
                "no one does anything",
                "no one is doing anything",
                "done that",
                "have done that",
                "already raised",
                "already complained",
                "already contacted",
                "already contacted amazon",
                "still no response",
                "no response",
                "not getting any response",
                "not getting any email response",
                "fifth time",
                "9th time",
                "ninth time",
                "again and again",
                "multiple times",
                "several times",
            ]

            if any(
                signal in text
                for signal in complaint_escalation_signals
            ):
                return (
                    "escalate",
                    "The customer indicates an unresolved complaint, repeated unsuccessful support, dissatisfaction requiring intervention, or insufficient context for safe automatic handling.",
                )

            if similarity >= 0.70:
                return (
                    "auto_handle",
                    "The complaint is sufficiently similar to historical support conversations and does not show a strong unresolved-support signal.",
                )

            return (
                "escalate",
                "The historical evidence is not sufficiently strong for safe automatic handling of the complaint.",
            )

        # =====================================================
        # PRIME MEMBERSHIP
        # =====================================================

        if intent == "prime_membership":

            prime_escalation_signals = [
                "charged",
                "charge",
                "refund",
                "cancel",
                "cancelled",
                "canceled",
                "renewal",
                "renewed",
                "problem",
                "issue",
                "not working",
                "cannot",
                "can't",
                "unable",
                "charged me",
                "subscription issue",
                "membership issue",
                "urgent",
                "asap",
            ]

            if any(
                signal in text
                for signal in prime_escalation_signals
            ):
                return (
                    "escalate",
                    "The Prime membership message involves a transaction, cancellation, or unresolved account-specific issue.",
                )

            if similarity >= 0.70:
                return (
                    "auto_handle",
                    "The Prime membership question is sufficiently similar to historical informational support conversations.",
                )

            return (
                "escalate",
                "There is insufficient historical evidence for safe automatic handling of this Prime membership request.",
            )

        # =====================================================
        # PRODUCT
        # =====================================================

        if intent == "product_issue":

            product_escalation_signals = [
                "refund",
                "charged",
                "wrong",
                "missing",
                "damaged",
                "broken",
                "defective",
                "not working",
                "doesn't work",
                "doesnt work",
                "won't work",
                "wont work",
                "cancel",
                "urgent",
                "asap",
                "call",
                "complaint",
                "customer service",
                "helpless",
                "no answer",
                "counterfeit",
                "fake",
                "not as described",
                "looks different",
                "different color",
                "wrong color",
                "wrong item",
            ]

            if any(
                signal in text
                for signal in product_escalation_signals
            ):
                return (
                    "escalate",
                    "The product issue appears case-specific, unresolved, or potentially requires return, refund, or human intervention.",
                )

            if similarity >= 0.70:
                return (
                    "auto_handle",
                    "The product question is sufficiently similar to historical product-support conversations and does not show a strong escalation signal.",
                )

            return (
                "escalate",
                "There is insufficient historical evidence for safe automatic handling of the product issue.",
            )

        # =====================================================
        # DEFAULT
        # =====================================================

        if similarity >= 0.70:
            return (
                "auto_handle",
                "The message is sufficiently similar to historical support conversations and no strong escalation signal was detected.",
            )

        return (
            "escalate",
            "There is insufficient historical evidence for safe automatic handling.",
        )

    def generate_response(
        self,
        customer_message,
        intent,
        retrieved_examples
    ):
        if not retrieved_examples:
            return (
                "I’m sorry you’re experiencing this. "
                "I’ll make sure your request is reviewed and handled appropriately."
            )

        best = retrieved_examples[0]

        historical_response = str(
            best.get("agent_response", "")
        ).strip()

        if not historical_response:
            return (
                "I’m sorry you’re experiencing this. "
                "I’ll make sure your request is reviewed and handled appropriately."
            )

        return historical_response

    def predict(self, customer_message):

        # -----------------------------------------------------
        # 1. CLASSIFY INTENT
        # -----------------------------------------------------

        intent = self.classifier.predict(
            customer_message
        )

        # -----------------------------------------------------
        # 2. RETRIEVE HISTORICAL EVIDENCE
        # -----------------------------------------------------

        retrieved_examples = self.retriever.retrieve(
            customer_message,
            intent=intent,
            top_k=3,
        )

        if retrieved_examples:
            best_similarity = retrieved_examples[0]["similarity"]
        else:
            best_similarity = 0.0

        # -----------------------------------------------------
        # 3. DECIDE AUTO-HANDLE / ESCALATE
        # -----------------------------------------------------

        decision, reason = self.decide(
            customer_message,
            intent,
            best_similarity,
        )

        # -----------------------------------------------------
        # 4. GENERATE GROUNDED RESPONSE
        # -----------------------------------------------------

        suggested_response = self.generate_response(
            customer_message,
            intent,
            retrieved_examples,
        )

        # -----------------------------------------------------
        # 5. EVIDENCE
        # -----------------------------------------------------

        if retrieved_examples:

            best = retrieved_examples[0]

            evidence = {
                "customer_message": best["customer_message"],
                "agent_response": best["agent_response"],
                "intent": best["intent"],
                "similarity": best["similarity"],
            }

        else:

            evidence = {
                "customer_message": "",
                "agent_response": "",
                "intent": "",
                "similarity": 0.0,
            }

        # -----------------------------------------------------
        # 6. RETURN COMPLETE RESULT
        # -----------------------------------------------------

        return {
            "customer_message": customer_message,
            "intent": intent,
            "decision": decision,
            "response": suggested_response,
            "suggested_response": suggested_response,
            "reason": reason,
            "evidence": evidence,
        }

    def handle(self, customer_message):
        return self.predict(customer_message)

