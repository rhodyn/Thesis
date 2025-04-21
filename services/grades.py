import joblib
import numpy as np

model = joblib.load("models/grade_predictor.pkl")

def predict(data):
    scores = np.array(data["scores"]).reshape(1, -1)
    prediction = model.predict(scores)[0]
    return {"predicted_grade": prediction}
