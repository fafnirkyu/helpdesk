import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. Load your data
df = pd.read_csv('data/Bitext.csv')
model = SentenceTransformer('all-MiniLM-L6-v2') # Use the same model as AWS
# 2. Generate the embeddings (This is the slow part)
print("Generating embeddings locally...")
embeddings = model.encode(df['instruction'].tolist(), show_progress_bar=True)
# 3. Save to a compressed numpy file
# This turns 26k vectors into one single file
np.savez_compressed('data/kb_embs.npz', embeddings=embeddings)
print("Done!")