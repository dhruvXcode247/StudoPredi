from flask import Flask, render_template, request, redirect, session
import joblib
import numpy as np
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "secret123"

# Load model
model = joblib.load("student_model.pkl")

# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = pd.read_csv("users.csv")

        user = users[(users["username"] == username) & (users["password"] == password)]

        if not user.empty:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    file_path = "Cleaned_student_data_.csv"

    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame()

    total = len(df)
    excellent = (df["Grading"] == "Excellent").sum() if not df.empty else 0
    average = (df["Grading"] == "Average").sum() if not df.empty else 0
    weak = (df["Grading"] == "Weak").sum() if not df.empty else 0

    return render_template(
        "dashboard.html",
        total=total,
        excellent=excellent,
        average=average,
        weak=weak
    )


# ================= PREDICT =================
@app.route("/predict", methods=["POST"])
def predict():
    if "user" not in session:
        return redirect("/")

    student_id = request.form["StudentID"]

    qs = float(request.form["QuestionsSolved"])
    score = float(request.form["AssessmentScore"])
    attendance = float(request.form["Attendance"])
    cgpa = float(request.form["CGPA"])
    hack = float(request.form["HackathonsParticipated"])

    features = np.array([[qs, score, attendance, hack, cgpa]])
    prediction = model.predict(features)[0]

    new_data = {
        "StudentID": str(student_id),
        "QuestionsSolved": qs,
        "Assessment Score": score,
        "Attendance": attendance,
        "HackathonsParticipated": hack,
        "CGPA": cgpa,
        "Grading": prediction
    }

    file_path = "Cleaned_student_data_.csv"

    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        df["StudentID"] = df["StudentID"].astype(str)

        if str(student_id) in df["StudentID"].values:
            mask = df["StudentID"] == str(student_id)
            for col, val in new_data.items():
                df.loc[mask, col] = val
        else:
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    else:
        df = pd.DataFrame([new_data])

    df.to_csv(file_path, index=False)

    # ===== HISTORY TRACKING =====
    history_file = "history.csv"

    history_row = {
        "StudentID": student_id,
        "PredictedGrade": prediction,
        "Time": pd.Timestamp.now()
    }

    if os.path.isfile(history_file):
        hist = pd.read_csv(history_file)
        hist = pd.concat([hist, pd.DataFrame([history_row])], ignore_index=True)
    else:
        hist = pd.DataFrame([history_row])

    hist.to_csv(history_file, index=False)

    return redirect("/dashboard")


# ================= SEARCH =================
@app.route("/search", methods=["POST"])
def search():
    if "user" not in session:
        return redirect("/")

    student_id = request.form["StudentID"]

    df = pd.read_csv("Cleaned_student_data_.csv")
    df["StudentID"] = df["StudentID"].astype(str)

    result = df[df["StudentID"] == student_id]

    return render_template("dashboard.html", result=result.to_dict(orient="records"))


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)