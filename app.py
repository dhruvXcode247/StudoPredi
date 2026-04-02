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

    os.makedirs("tmp", exist_ok=True)
    file_path = os.path.join("tmp", "Cleaned_student_data_.csv")

    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame()

    total = len(df)
    excellent = (df["Grading"] == "Excellent").sum() if not df.empty else 0
    average = (df["Grading"] == "Average").sum() if not df.empty else 0
    weak = (df["Grading"] == "Weak").sum() if not df.empty else 0

    # 🔥 Chart data
    chart_labels = ["Excellent", "Average", "Weak"]
    chart_values = [int(excellent), int(average), int(weak)]

    prediction_text = session.pop("prediction", None)

    return render_template(
        "dashboard.html",
        total=total,
        excellent=excellent,
        average=average,
        weak=weak,
        prediction_text=prediction_text,
        chart_labels=chart_labels,
        chart_values=chart_values
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

    os.makedirs("tmp", exist_ok=True)
    file_path = os.path.join("tmp", "Cleaned_student_data_.csv")

    # create file if not exists
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=new_data.keys())
        df.to_csv(file_path, index=False)

    df = pd.read_csv(file_path)
    df["StudentID"] = df["StudentID"].astype(str)

    # update or insert
    if str(student_id) in df["StudentID"].values:
        mask = df["StudentID"] == str(student_id)
        for col, val in new_data.items():
            df.loc[mask, col] = val
    else:
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

    df.to_csv(file_path, index=False)

    # ================= HISTORY =================
    history_file = os.path.join("tmp", "history.csv")

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

    session["prediction"] = f"Predicted Grade: {prediction} for Student ID: {student_id}"

    return redirect("/dashboard")


# ================= SEARCH =================
@app.route("/search", methods=["POST"])
def search():
    if "user" not in session:
        return redirect("/")

    student_id = request.form["StudentID"]

    os.makedirs("tmp", exist_ok=True)
    file_path = os.path.join("tmp", "Cleaned_student_data_.csv")

    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        df["StudentID"] = df["StudentID"].astype(str)
        result = df[df["StudentID"] == student_id]
    else:
        df = pd.DataFrame()
        result = pd.DataFrame()

    if not df.empty and "Grading" in df.columns:
        total = int(len(df))
        excellent = int((df["Grading"] == "Excellent").sum())
        average = int((df["Grading"] == "Average").sum())
        weak = int((df["Grading"] == "Weak").sum())
    else:
        total = excellent = average = weak = 0

    chart_labels = ["Excellent", "Average", "Weak"]
    chart_values = [excellent, average, weak]

    return render_template(
        "dashboard.html",
        total=total,
        excellent=excellent,
        average=average,
        weak=weak,
        chart_labels=chart_labels,
        chart_values=chart_values,
        result=result.to_dict(orient="records")
    )


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)