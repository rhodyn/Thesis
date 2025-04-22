# Import required libraries
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib
import os

vectorizer_path = os.path.join("models", "vectorizer.pkl")
model_path = os.path.join("models", "naive_bayes-model.pkl")

vectorizer = joblib.load(vectorizer_path)
model = joblib.load(model_path)

def recommend_hobby(user_input):
    X = vectorizer.transform([user_input])
    prediction = model.predict(X)
    return prediction[0]
