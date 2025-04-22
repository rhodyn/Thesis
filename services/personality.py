# Import required libraries
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import joblib

# Load model and data values
data = joblib.load('models/cbf-personality_model.pkl')
courses = data['courses']
person_numeric = data['numeric_features']

# Predict function
def recommend_person(user_input):
    
    # Stores input as array
    student_data = np.array([[user_input]])

    # Compute cosine simularity with all courses
    similarities = cosine_similarity(student_data, person_numeric)[0]

    # Combine results
    results = list(zip(courses, similarities))

    # Sort by similarity score
    results.sort(key=lambda x: x[1], reverse=True)

    return results[0]