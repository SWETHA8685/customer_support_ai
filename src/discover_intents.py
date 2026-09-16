import pandas as pd
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


# Load customer messages
df = pd.read_csv(
    "data/processed/amazonhelp_conversations.csv",
    usecols=["customer_message"]
)

# Remove empty messages
df = df.dropna(subset=["customer_message"])


def clean_text(text):
    text = str(text)

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)

    # Remove @mentions
    text = re.sub(r"@\w+", " ", text)

    # Remove HTML entities
    text = re.sub(r"&\w+;", " ", text)

    # Keep letters and spaces
    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    # Convert to lowercase
    text = text.lower()

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# Clean messages
df["clean_message"] = df["customer_message"].apply(clean_text)

# Remove very short messages
df = df[df["clean_message"].str.len() >= 15]

# Take a manageable sample
sample = df.sample(
    n=min(10000, len(df)),
    random_state=42
)

# Convert text to TF-IDF features
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=5000,
    ngram_range=(1, 2)
)

X = vectorizer.fit_transform(sample["clean_message"])


# Create clusters
kmeans = KMeans(
    n_clusters=8,
    random_state=42,
    n_init=10
)

sample["cluster"] = kmeans.fit_predict(X)


# Display important words
terms = vectorizer.get_feature_names_out()

print("\nDISCOVERED TOPICS\n")

for cluster_number in range(8):

    center = kmeans.cluster_centers_[cluster_number]

    top_indices = center.argsort()[-12:][::-1]

    words = [terms[i] for i in top_indices]

    print(f"Cluster {cluster_number}:")
    print(", ".join(words))
    print()