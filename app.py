from flask import Flask, render_template, request
import joblib
import numpy as np
import pandas as pd
import os

app = Flask(__name__)

# Load model
model = joblib.load("student_model.pkl")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    # 🔹 Get form data
    student_id = request.form["StudentID"]

    qs = float(request.form["QuestionsSolved"])
    score = float(request.form["AssessmentScore"])
    attendance = float(request.form["Attendance"])
    cgpa = float(request.form["CGPA"])
    hack = float(request.form["HackathonsParticipated"])

    # 🔹 Prediction
    features = np.array([[qs, score, attendance, hack, cgpa]])
    prediction = model.predict(features)[0]

    # 🔹 Create row data
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

    # 🔥 If file exists
    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)

        # Ensure StudentID is string
        df["StudentID"] = df["StudentID"].astype(str)

        # 🔁 If student exists → UPDATE FULL ROW
        if str(student_id) in df["StudentID"].values:
            mask = df["StudentID"] == str(student_id)
            for col, val in new_data.items():
                df.loc[mask, col] = val
        else:
            # ➕ Add new row
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

        df.to_csv(file_path, index=False)

    # 🔥 If file does NOT exist → create new
    else:
        df = pd.DataFrame([new_data])
        df.to_csv(file_path, index=False)

    return render_template(
        "index.html",
        prediction_text=f"Predicted Grade: {prediction} for Student ID: {student_id}"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)