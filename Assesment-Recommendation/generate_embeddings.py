from sentence_transformers import SentenceTransformer
import pandas as pd

df = pd.read_csv("shl_assessments.csv")

model = SentenceTransformer("all-MiniLM-L6-v2")

df["embedding"] = df["Name"].apply(lambda x: model.encode(x).tolist())

df.to_pickle("shl_assessments_with_embeddings.pkl")
