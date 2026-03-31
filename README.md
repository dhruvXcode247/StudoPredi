# 🎓 StudoPredi - Student Performance Prediction System

A Machine Learning web application that predicts a student's performance category (**Excellent, Average, Weak**) based on academic and activity-related features.

Deployed using **Flask** and hosted on Render.

---

## 🚀 Features

- 📊 Predict student performance using ML model
- 🔄 Update existing student records using StudentID
- ➕ Add new student data automatically
- 💾 Store predictions in CSV file
- 🌐 Web-based interface using Flask

---

## 🧠 Machine Learning Model

- Algorithm: **Random Forest Classifier**
- Features used:
  - Questions Solved
  - Assessment Score
  - Attendance
  - CGPA
  - Hackathons Participated

- Output:
  - Weak
  - Average
  - Excellent

---


---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

    git clone https://github.com/dhruvXcode247/StudoPredi

    cd StudoPredi2

### 2️⃣ Install dependencies

    pip install -r requirements.txt

### 3️⃣ Run the application

    python app.py

### 4️⃣ Open in browser

    http://127.0.0.1:5000/
