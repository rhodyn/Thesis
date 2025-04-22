# Import required libraries
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os

# Read file input
df = pd.read_csv("personality.csv")

# Labels
courses = df["Course"]
features = df.drop(columns=["Course"]).values

# Compute cosine similarity between user and each course
similarities = cosine_similarity(features)

# Save the numeric matrix and course names
label_data = {
    'courses': courses,
    'numeric_features':features,
    'similarity_matrix': similarities
}

# Exports the trained model to pkl file
os.makedirs('models', exist_ok=True)
joblib.dump(label_data, 'models/cbf_personality-model.pkl')
print("Content based filtering model (Personality) saved to models/cbf_personality-model.pkl")