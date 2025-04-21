from flask import Flask, request, jsonify
from services import course, grades, interests

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Multi-Model ML API!"

@app.route('/recommend_course', methods=['POST'])
def recommend_course():
    data = request.get_json()
    result = course.predict(data)
    return jsonify(result)

@app.route('/predict_grade', methods=['POST'])
def predict_grade():
    data = request.get_json()
    result = grades.predict(data)
    return jsonify(result)

@app.route('/classify_interest', methods=['POST'])
def classify_interest():
    data = request.get_json()
    result = interests.predict(data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
