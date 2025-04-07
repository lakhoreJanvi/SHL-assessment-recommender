from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load data and model
df = pd.read_pickle("shl_assessments_with_embeddings.pkl")
model = SentenceTransformer("all-MiniLM-L6-v2")

app = FastAPI(title="SHL Assessment Recommendation API")

class RecommendationResponse(BaseModel):
    Name: str
    Link: str
    Duration: int
    Test_Type: str
    Remote_testing: bool
    Adaptive_IRT: str

@app.get("/recommend", response_model=List[RecommendationResponse])
def recommend_assessments(query: str = Query(..., description="Job description or requirement")):
    query_emb = model.encode(query).reshape(1, -1)
    emb_matrix = np.vstack(df["embedding"].to_numpy())
    similarities = cosine_similarity(query_emb, emb_matrix)[0]
    top_indices = similarities.argsort()[::-1][:10]
    print(df.columns)
    try:
        results = df.iloc[top_indices][["Name", "Assessment Link", "Duration (min)", "Test Type", "Remote testing", "Adaptive/IRT"]]
    except KeyError as e:
        print(f"Column not found: {e}")
        return {"error": f"Column not found: {e}"}
    
    results = df.iloc[top_indices][["Name", "Assessment Link", "Duration (min)", "Test Type", "Remote testing", "Adaptive/IRT"]]
    results.columns = ["Name", "Link", "Duration", "Test_Type", "Remote_testing", "Adaptive_IRT"]
    
    results["Remote_testing"] = results["Remote_testing"].astype(bool)
    results["Adaptive_IRT"] = results["Adaptive_IRT"].apply(lambda x: str(x))
    
    return results.to_dict(orient="records")
