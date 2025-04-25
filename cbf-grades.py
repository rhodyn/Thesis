# Import required libraries
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import re
import joblib
import os

# Output float precision
pd.set_option('display.precision', 5)

# Read file input
data = pd.read_csv('cbf-test.csv', dtype=str)

# Extract grade ranges from text input
def extract_range_average(text):
    try:
        # Find numbers like 85-90
        match = re.search(r'(\d+)\s*-\s*(\d+)', text)
        if match:
            low = float(match.group(1))
            high = float(match.group(2))
            return (low + high) / 2
    except:
        pass
    return None  # Return None if pattern not found

# Convert subject column
subject_columns = ['Math', 'Science', 'English', 'NCAE']
for col in subject_columns:
    data[col] = data[col].apply(extract_range_average)

# Labels
X = data[subject_columns].values
courses = data['Course'].values

# Compute cosine similarity
similarities = cosine_similarity(X)

# Save the numeric matrix and course names
label_data = {
    'courses': courses,
    'numeric_features': X,
    'similarity_matrix': similarities
}

# Exports the trained model to pkl file
os.makedirs('models', exist_ok=True)
joblib.dump(label_data, 'models/cbf_grades-model.pkl')
print("Content based filtering model (Grades) saved to models/cbf_grades-model.pkl")