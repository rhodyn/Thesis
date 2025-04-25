from flask import Flask, request, jsonify, render_template, session, request, redirect, url_for
from services import hobby, grades, personality
import numpy as np
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_dev_key") # Required for sessions

# Loads index page
@app.route('/')
def home():
    return render_template('index.html')

# Validates username input on index before moving to next page
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]

    if username:  # Accepts non empty values
        session["logged_in"] = True
        session["username"] = username  # Store username
        return redirect(url_for("strandprofile"))  
    return "Username cannot be empty."

def login_required(route_func):
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("/"))
        return route_func(*args, **kwargs)
    wrapper.__name__ = route_func.__name__
    return wrapper

# Strand profile page (Page 1 of user input)
@app.route("/strandprofile", methods=["GET", "POST"])
@login_required
def strandprofile():
    if request.method == "POST":
        import json
        json_input = request.form.get("student_input_array", "[]")
        inputs = json.loads(json_input)
        session["profile"] = inputs # Store in session for later use
        return redirect(url_for("hobbies"))
    return render_template("strandprofile.html")

# Hobbies page (Page 2 of user input)
@app.route("/hobbies", methods=["GET", "POST"])
@login_required
def hobbies():
    if request.method == "POST":
        import json
        raw_input = request.form.get("text_inputs", "{}")
        user_inputs = json.loads(raw_input)

        # Get input values
        parts = [
            user_inputs.get("hobby", ""),
            user_inputs.get("interest1", ""),
            user_inputs.get("interest2", ""),
            user_inputs.get("interest3", ""),
            user_inputs.get("career", "")
        ]

        # Combine into a single sentence
        combined_text = " ".join(part.strip() for part in parts if part.strip())

        # Store in session for later use
        session["hobbies"] = combined_text

        return redirect(url_for("studentgrade"))
    return render_template("hobbies.html")

# Student grade page (Page 3 of user input)
@app.route("/studentgrade", methods=["GET", "POST"])
@login_required
def studentgrade():
    if request.method == "POST":
        user_input = {
            'Math': request.form['Math'],
            'Science': request.form['Science'],
            'English': request.form['English'],
            'NCAE': request.form['NCAE'],
        }
        session["grade"] = user_input
        return redirect(url_for("personality_test"))
    return render_template("studentgrade.html")

# Personality page (Page 4 of user input)
@app.route("/personality_test", methods=["GET", "POST"])
@login_required
def personality_test():
    if request.method == "POST":
        # user_input = {
        #     'Extraversion': float(request.form['E']),
        #     'Agreeableness': float(request.form['A']),
        #     'Conscientiousness': float(request.form['C']),
        #     'Neuroticism': float(request.form['N']),
        #     'Openness': float(request.form['O'])
        # }
        # session["personality"] = user_input

        scores = request.form.get("bfi_scores")
        if scores:
            score_array = eval(scores)  # Turn string into list
            session["personality"] = score_array
        return redirect(url_for("result"))
    return render_template("bfi-test.html")

# Results page (Page 5)
@app.route("/result", methods=["GET", "POST"])
@login_required
def result():
    # Loading data collected from user input pages
    input1 = session.get("hobbies", "")
    input2 = session.get("grade", {})
    input3 = session.get("personality", [])

    # Model prediction with collected user input
    hobby_final = hobby.recommend_hobby(input1)
    grade_final = grades.recommend_grade(input2)
    person_final = personality.recommend_person(input3)

    return render_template("results.html", hobby_final=hobby_final, grade_final=grade_final, person_final=person_final)

if __name__ == "__main__":
    app.run(debug=True)
##############################################################################################

# @app.route('/recommend_grade', methods=['GET', 'POST'])
# def recommend_grade():
#     if request.method == 'POST':
#         try:
#             # scores = request.form.get('scores_course') or request.json.get('scores')
#             # scores = [float(x.strip()) for x in scores.split(',')]
#             # result = course.predict({"scores": scores})
#             # return jsonify(result) if request.is_json else render_template('result.html', result=f"Recommended Course: {result['recommended_course']}")

#             user_input = {
#                 'Math': request.form['Math'],
#                 'English': request.form['English'],
#                 'Science': request.form['Science'],
#                 'NCAE': request.form['NCAE'],
#             }

#             recommendation = recommend_grade(user_input)
#         except Exception as e:
#             return str(e), 400
#     return render_template('recommend_course.html', recommendation=recommendation)

# @app.route('/recommend_person', methods=['GET', 'POST'])
# def recommend_person():
#     if request.method == 'POST':
#         try:
#             # scores = request.form.get('scores_grade') or request.json.get('scores')
#             # scores = [float(x.strip()) for x in scores.split(',')]
#             # result = grades.predict({"scores": scores})
#             # return jsonify(result) if request.is_json else render_template('result.html', result=f"Predicted Grade: {result['predicted_grade']}")

#             user_input = {
#                 'Extraversion': float(request.form['E']),
#                 'Agreeableness': float(request.form['A']),
#                 'Conscientiousness': float(request.form['C']),
#                 'Neuroticism': float(request.form['N']),
#                 'Openness': float(request.form['O'])
#             }

#             recommendation = recommend_person(user_input)
#         except Exception as e:
#             return str(e), 400
#     return render_template('predict_grade.html', recommendation=recommendation)

# @app.route('/recommend_hobby', methods=['GET', 'POST'])
# def recommend_hobby():
#     if request.method == 'POST':
#         try:
#             # scores = request.form.get('scores_interest') or request.json.get('scores')
#             # scores = [float(x.strip()) for x in scores.split(',')]
#             # result = interests.predict({"scores": scores})
#             # return jsonify(result) if request.is_json else render_template('result.html', result=f"Interest Category: {result['interest_category']}")

#             user_text = request.form.get("student_input", "")
#             recommendation = recommend_hobby(user_text)

#         except Exception as e:
#             return str(e), 400
#     return render_template('recommend_result.html',recommendation=recommendation)