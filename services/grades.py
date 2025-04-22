# Import required libraries
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import re

# Load model and data values
data = joblib.load('models/cbf-grades_model.pkl')
courses = data['courses']
grades_numeric = data['numeric_features']

# Predict function
def recommend_grade(user_input):
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
    
    # Convert student input into a numeric feature vector
    student_data = [extract_range_average(text) for text in user_input]
    student_data = [student_data]
    
     # Compute cosine similarity with all courses
    similarities = cosine_similarity(student_data, grades_numeric)

    # Get most similar course
    best_match_index = np.argmax(similarities)
    return courses.iloc[best_match_index]['Course']