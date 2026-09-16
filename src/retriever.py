import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_FILE = "data/processed/amazonhelp_training.csv"
GOLDEN_FILE = "data/golden/golden_set.csv"


class HistoricalResponseRetriever:

    def __init__(
        self,
        data_file=DATA_FILE,
        golden_file=GOLDEN_FILE
    ):
        print("Loading historical AmazonHelp conversations...")

        # Load historical training conversations
        self.df = pd.read_csv(data_file).dropna(
            subset=[
                "customer_message",
                "agent_response",
                "intent"
            ]
        ).copy()

        print(
            "Historical conversations before leakage removal:",
            len(self.df)
        )

        # ==========================================================
        # REMOVE GOLDEN-SET EXAMPLES
        # ==========================================================
        # The golden examples must not be available to the retriever.
        # Otherwise the retriever may retrieve the exact test example,
        # producing artificially high similarity scores.
        try:

            golden_df = pd.read_csv(golden_file).dropna(
                subset=["customer_message"]
            )

            golden_messages = set(
                golden_df["customer_message"]
                .astype(str)
                .str.strip()
            )

            before = len(self.df)

            self.df = self.df[
                ~self.df["customer_message"]
                .astype(str)
                .str.strip()
                .isin(golden_messages)
            ].copy()

            removed = before - len(self.df)

            print(
                "Golden examples removed from retrieval index:",
                removed
            )

        except FileNotFoundError:

            print(
                "Warning: golden set not found. "
                "Leakage removal was skipped."
            )

        # Reset index after removing golden examples
        self.df.reset_index(drop=True, inplace=True)

        print(
            "Historical conversations available for retrieval:",
            len(self.df)
        )

        # ==========================================================
        # TF-IDF INDEX
        # ==========================================================

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            max_features=50000
        )

        print("Building retrieval index...")

        self.matrix = self.vectorizer.fit_transform(
            self.df["customer_message"]
        )

        print("Retriever ready.")

    # ==============================================================
    # RETRIEVE HISTORICAL RESPONSES
    # ==============================================================

    def retrieve(
        self,
        customer_message,
        intent=None,
        top_k=3
    ):

        # ----------------------------------------------------------
        # Filter by intent when possible
        # ----------------------------------------------------------

        if intent is not None:

            filtered_df = self.df[
                self.df["intent"] == intent
            ].copy()

            # If no examples exist for this intent,
            # fall back to the complete historical dataset.
            if len(filtered_df) == 0:
                filtered_df = self.df.copy()

        else:

            filtered_df = self.df.copy()

        # ----------------------------------------------------------
        # Convert customer message into TF-IDF vector
        # ----------------------------------------------------------

        query_vector = self.vectorizer.transform(
            [customer_message]
        )

        # ----------------------------------------------------------
        # Get candidate indexes
        # ----------------------------------------------------------

        candidate_indices = filtered_df.index

        candidate_matrix = self.matrix[
            candidate_indices
        ]

        # ----------------------------------------------------------
        # Calculate cosine similarity
        # ----------------------------------------------------------

        similarities = cosine_similarity(
            query_vector,
            candidate_matrix
        ).flatten()

        # ----------------------------------------------------------
        # Get top K results
        # ----------------------------------------------------------

        top_positions = similarities.argsort()[
            -top_k:
        ][::-1]

        results = []

        for position in top_positions:

            original_index = candidate_indices[position]

            results.append(
                {
                    "customer_message": self.df.loc[
                        original_index,
                        "customer_message"
                    ],

                    "agent_response": self.df.loc[
                        original_index,
                        "agent_response"
                    ],

                    "intent": self.df.loc[
                        original_index,
                        "intent"
                    ],

                    "similarity": float(
                        similarities[position]
                    )
                }
            )

        return results


# ==============================================================
# TEST RETRIEVER
# ==============================================================

if __name__ == "__main__":

    retriever = HistoricalResponseRetriever()

    test_cases = [

        (
            "My package says delivered "
            "but I never received it.",
            "delivery_not_received"
        ),

        (
            "I want to know how much "
            "Amazon Prime costs.",
            "prime_membership"
        ),

        (
            "I cannot login to "
            "my Amazon account.",
            "account_issue"
        ),

        (
            "My Amazon Pay payment failed.",
            "payment_issue"
        )
    ]

    for message, intent in test_cases:

        print("\n")
        print("=" * 60)
        print("TEST CASE")
        print("=" * 60)

        print("\nCustomer:")
        print(message)

        print("\nIntent:")
        print(intent)

        results = retriever.retrieve(
            message,
            intent=intent,
            top_k=3
        )

        for i, result in enumerate(
            results,
            start=1
        ):

            print("\nResult", i)

            print(
                "Similarity:",
                round(
                    result["similarity"],
                    3
                )
            )

            print(
                "Intent:",
                result["intent"]
            )

            print(
                "Customer:",
                result["customer_message"]
            )

            print(
                "AmazonHelp:",
                result["agent_response"]
            )