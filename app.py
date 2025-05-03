from flask import Flask, request, jsonify, render_template, session, request, redirect, url_for, make_response, flash
from services import hobby, grades, personality
import numpy as np
import os
import csv
import re
from collections import Counter
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_dev_key") # Required for sessions

# Loads database and required data variables
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_data.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class UserResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    profile = db.Column(db.String(1000))  
    hobbies = db.Column(db.String(10000))
    grade = db.Column(db.String(1000))
    personality_result = db.Column(db.String(100))
    recommendation = db.Column(db.String(500))
    feedback = db.Column(db.Integer)  # 1 for True/Yes, 0 for False/No

    def __init__(self, username, profile, hobbies, grade, personality_result, recommendation, feedback):
        self.username = username
        self.profile = profile
        self.hobbies = hobbies
        self.grade = grade
        self.personality_result = personality_result
        self.recommendation = recommendation
        self.feedback = feedback

# Loads index page
@app.route('/')
def home():
    return render_template('index.html')

# Validates username input on index before moving to next page
@app.route("/login", methods=["GET", "POST"])
def login():
    # List of admin emails
    ADMIN_EMAILS = ['rances.christianalexandra@ue.edu.ph', 'lopez.adrian1@ue.edu.ph', 'rosaldo.asiadominic@ue.edu.ph','baris.sherwin@ue.edu.ph','sipe.rasselavielrodyn@ue.edu.ph','rex.bringula@ue.edu.ph']
    ADMIN_PASSWORD = 'admin123'
    
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')  # important!

        if role == "Continue":
            # User login logic
            session["logged_in"] = True
            session['username'] = username
            return redirect(url_for("strandprofile"))  # or wherever your user dashboard is
        
        elif role == "Login":
            # Admin login logic
            if username in ADMIN_EMAILS and password == ADMIN_PASSWORD:
                session['admin'] = True
                return redirect('/view_submissions')
            else:
                flash("Invalid admin credentials. Please try again.")
                return redirect(url_for("home"))
        
        else:
            return "Unknown role", 400
    return "Username cannot be empty."
     

def login_required(route_func):
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("home"))
        return route_func(*args, **kwargs)
    wrapper.__name__ = route_func.__name__
    return wrapper

def admin_required(route_func):
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("home"))
        return route_func(*args, **kwargs)
    wrapper.__name__ = route_func.__name__
    return wrapper

# Strand profile page (Page 1 of user input)
@app.route("/strandprofile", methods=["GET", "POST"])
@login_required
def strandprofile():
    if request.method == "POST":
        import json
        user_data = request.form.get('user_data')
        print("Raw user_data:", user_data)
        if user_data:
            try:
                data_array = json.loads(user_data)  # Convert JSON string to list
                session['profile'] = data_array   # Save to session
            except json.JSONDecodeError:
                return "Invalid data format received", 400
        return redirect(url_for('hobbies'))
    return render_template("strandprofile1.html")

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
        import json
        grades_json = request.form.get("grades")
        if grades_json:
            grade_array = json.loads(grades_json)
            session["grade"] = grade_array 
        return redirect(url_for("personality_test"))
    return render_template("studentgrade.html")

# Personality page (Page 4 of user input)
@app.route("/personality_test", methods=["GET", "POST"])
@login_required
def personality_test():
    if request.method == "POST":
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
    input2 = session.get("grade", [])
    input3 = session.get("personality", [])

    feedback_text = request.form.get("feedback")
    session["feedback"] = feedback_text

    # Model prediction with collected user input
    hobby_final = hobby.recommend_hobby(input1)
    grade_final = grades.recommend_grade(input2)
    person_final = personality.recommend_person(input3)

    model_predictions = {
        "Hobbies": hobby_final,
        "Grades": grade_final,
        "Personality Type": person_final
    }

    # Map the model name to their output
    course_to_models = {}
    if hobby_final in course_to_models:
        course_to_models[hobby_final].append("Hobbies")
    else:
        course_to_models[hobby_final] = ["Hobbies"]

    if grade_final in course_to_models:
        course_to_models[grade_final].append("Grades")
    else:
        course_to_models[grade_final] = ["Grades"]

    if person_final in course_to_models:
        course_to_models[person_final].append("Personality Type")
    else:
        course_to_models[person_final] = ["Personality Type"]

    model_result = [hobby_final, grade_final, person_final]
    count = Counter(model_result)
    most_common_course, frequency = count.most_common(1)[0]

    if frequency == 3:
        final_recommendation = [most_common_course]
        message = f"Based on the Recommendation System, you are very suitable for '{most_common_course}'. More details can be found in \"Learn More \"."
    elif frequency == 2:
        final_recommendation = [most_common_course]
        message = f"Based on the Recommendation System, you have good compatibility for '{most_common_course}'. More details can be found in \"Learn More \"."
    else:
        final_recommendation = model_result
        message = "It seems that you don't have high compatibility with a certain IT Degree Course. Regardless, here are some you can consider. More details can be found in \"Learn More \"."

    session["recommendation"] = final_recommendation

    # example when all session data is ready
    username = session.get('username')
    profile = session.get('profile')
    hobbies = session.get('hobbies')
    grade = session.get('grade')
    personality_result = session.get('personality')

    full_recommendations = session.get('recommendation', [])
    acronyms_only = [re.search(r"\((.*?)\)", rec).group(1) if "(" in rec else rec for rec in full_recommendations]
    recommendation = ", ".join(acronyms_only)

    # Save to database
    new_result = UserResult(username=username, profile=str(profile), hobbies=str(hobbies), grade=str(grade), personality_result=str(personality_result), recommendation=str(recommendation), feedback=None )
    db.session.add(new_result)
    db.session.commit()

    session['last_result_id'] = new_result.id

    return render_template("results.html", recommendations=final_recommendation, message=message, course_sources=course_to_models)

@app.route('/submit_feedback', methods=['POST'])
@login_required
def submit_feedback():
    feedback_raw = request.form.get('feedback', 'false')
    feedback_clean = feedback_raw.strip().lower()

    print(f"RAW feedback from form: {repr(feedback_raw)} (type: {type(feedback_raw)})")
    print(f"Cleaned feedback: {feedback_clean}")

    feedback_value = 1 if feedback_raw == 'true' else 0

    result_id = session.get('last_result_id')
    print(f"Result ID: {result_id}")

    if result_id is None:
        flash("Unable to identify which result to update feedback for.", "error")
        return redirect(url_for("view_submissions"))

    user_entry = UserResult.query.get(result_id)
    if user_entry:
        print(f"Before update: feedback={user_entry.feedback}")
        user_entry.feedback = feedback_value
        db.session.commit()
        print(f"After update: feedback={user_entry.feedback}")
        flash("Feedback submitted successfully!", "success")
    else:
        flash("Result not found.", "error")

    return redirect(url_for("view_submissions"))

@app.route("/view_submissions", methods=["GET", "POST"])
@admin_required
def view_submissions():
    db.session.expire_all()  # Force SQLAlchemy to reload from DB
    results = UserResult.query.all()
    return render_template("view_submissions.html", results=results)

@app.route('/download_csv')
@admin_required
def download_csv():
    results = UserResult.query.all()

    # Create a CSV in memory
    si = []
    si.append(["Profile", "Hobbies", "Grades", "Personality", "Recommendation","Feedback"])  # headers
    for user in results:
        si.append([user.profile, user.hobbies, user.grade, user.personality_result, user.recommendation, user.feedback])

    # Convert list to CSV formatted text
    output = ""
    for row in si:
        output += ",".join(f'"{item}"' for item in row) + "\n"

    # Send it as file download
    response = make_response(output)
    response.headers["Content-Disposition"] = "attachment; filename=user_submissions.csv"
    response.headers["Content-type"] = "text/csv"
    return response

@app.route("/delete_entry/<int:entry_id>", methods=["POST"])
@admin_required
def delete_entry(entry_id):
    entry = UserResult.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted successfully.", "success")
    return redirect(url_for('view_submissions'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/end_session', methods=['POST'])
@login_required
def end_session():
    session.clear()  # Clear all session data
    return redirect(url_for('home'))  # Redirect to the index route

@app.route("/debug_feedback")
def debug_feedback():
    all_results = UserResult.query.all()
    return "<br>".join([f"ID {r.id} → {r.feedback} ({type(r.feedback)})" for r in all_results])

if __name__ == "__main__":
    # with app.app_context():
    # # Check if 'feedback' column exists and convert boolean to integer if necessary
    #     from sqlalchemy import text

    #     # Optional: Print existing data types
    #     result = db.session.execute(text("PRAGMA table_info(user_result);"))
    #     print("Table schema for user_result:")
    #     for row in result.fetchall():
    #         print(row)

    #     # Manually update all existing True/False feedback values to 1/0
    #     db.session.execute(text("UPDATE user_result SET feedback = 1 WHERE feedback = 'True'"))
    #     db.session.execute(text("UPDATE user_result SET feedback = 0 WHERE feedback = 'False'"))
    #     db.session.commit()
    app.run(debug=True)
