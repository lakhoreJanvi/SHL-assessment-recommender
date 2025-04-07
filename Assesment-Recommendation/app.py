import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
    
df = pd.read_pickle("shl_assessments_with_embeddings.pkl")
model = SentenceTransformer("all-MiniLM-L6-v2")

st.title("🔍 SHL Assessment Recommender")

query = st.text_area("Enter job description or requirement:")
if st.button("Find Assessments") and query.strip():
    query_emb = model.encode(query).reshape(1, -1)
    emb_matrix = np.vstack(df["embedding"].to_numpy())
    
    similarities = cosine_similarity(query_emb, emb_matrix)[0]
    top_indices = similarities.argsort()[::-1][:10]

    results = df.iloc[top_indices][["Name", "Assessment Link", "Remote testing", "Adaptive/IRT", "Duration (min)", "Test Type"]]
    st.write("### Top Recommended Assessments")
    st.dataframe(results.reset_index(drop=True))
