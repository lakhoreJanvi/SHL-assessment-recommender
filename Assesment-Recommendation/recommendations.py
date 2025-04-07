import pandas as pd
from sentence_transformers import SentenceTransformer
from huggingface_hub.utils import snapshot_download

df = pd.read_csv("shl_assessments.csv")

expected_columns = ["Name", "Assessment Link", "Remote testing", "Adaptive/IRT", "Duration (min)", "Test Type"]
missing = [col for col in expected_columns if col not in df.columns]
if missing:
    print(f"Warning: Missing columns in CSV: {missing}")

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Use the 'Name' (or optionally also other fields) for semantic meaning
df["embedding"] = df["Name"].apply(lambda x: model.encode(str(x)).tolist())

# Save preprocessed version
df.to_pickle("shl_assessments_with_embeddings.pkl")
