import joblib
import numpy as np

model = joblib.load("models/interest_classifier.pkl")

def predict(data):
    scores = np.array(data["scores"]).reshape(1, -1)
    prediction = model.predict(scores)[0]
    return {"interest_category": prediction}
