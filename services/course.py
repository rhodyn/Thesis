import joblib
import numpy as np

model = joblib.load("models/course_recommender.pkl")

def predict(data):
    scores = np.array(data["scores"]).reshape(1, -1)
    prediction = model.predict(scores)[0]
    return {"recommended_course": prediction}
