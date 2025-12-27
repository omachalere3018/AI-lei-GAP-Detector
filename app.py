import sqlite3
import json
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.secret_key = "secret123"

load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment")

client = OpenAI(api_key=OPENAI_KEY)


# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            topic TEXT,
            score INTEGER,
            total INTEGER,
            time_taken INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# ✅ ADDED USERS TABLE (SIGNUP SUPPORT)
def init_users():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()
init_users()

# ---------------- LOGIN ----------------
TEACHERS = {
    "teacher": "teacher123",
    "admin": "admin123"
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mode = request.form.get("mode", "login")
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()

        # ---------------- SIGNUP ----------------
        if mode == "signup":
            try:
                c.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password)
                )
                conn.commit()
                conn.close()
                return render_template(
                    "login.html",
                    error="Signup successful! Please login."
                )
            except sqlite3.IntegrityError:
                conn.close()
                return render_template(
                    "login.html",
                    error="Username already exists"
                )

        # ---------------- TEACHER LOGIN ----------------
        if TEACHERS.get(username) == password:
            session["student_id"] = username
            return redirect(url_for("dashboard"))

        # ---------------- STUDENT LOGIN ----------------
        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = c.fetchone()
        conn.close()

        if user:
            session["student_id"] = username
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid Login")

    return render_template("login.html")

# ===

# @app.route("/signup", methods=["POST"])
# def signup():
#     email = request.form["email"]
#     password = request.form["password"]

#     user_ref = db.collection("users").document(email)
#     if user_ref.get().exists:
#         return render_template("login.html", error="User already exists")

#     user_ref.set({
#         "email": email,
#         "password": password,
#         "role": "student"
#     })

#     return redirect(url_for("login"))


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "student_id" not in session:
        return redirect(url_for("login"))
    return render_template("studentindex.html")

# ---------------- QUIZ PAGE ----------------
@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

# ---------------- AI QUIZ GENERATION ----------------
# @app.route("/generate-quiz", methods=["POST"])
# def generate_quiz():
#     data = request.json
#     subject = data.get("subject")
#     topic = data.get("topic")
#     difficulty = data.get("difficulty")

#     prompt = f"""
# Return ONLY valid JSON.
# Generate exactly 10 MCQs.

# FORMAT:
# [
#   {{
#     "question": "text",
#     "options": ["A", "B", "C", "D"],
#     "answer": "A"
#   }}
# ]

# SUBJECT: {subject}
# TOPIC: {topic}
# DIFFICULTY: {difficulty}
# """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.2
#         )

#         raw = response.choices[0].message.content.strip()
#         start = raw.find("[")
#         end = raw.rfind("]") + 1
#         quiz = json.loads(raw[start:end])

#         return jsonify(quiz)

#     except Exception as e:
#         print("Quiz generation error:", e)
#         return jsonify([])

# @app.route("/generate-quiz", methods=["POST"])
# def generate_quiz():
#     data = request.json
#     subject = data.get("subject")
#     topic = data.get("topic")
#     difficulty = data.get("difficulty")

#     prompt = f"""
# Return ONLY valid JSON.
# Generate exactly 10 MCQs.

# FORMAT:
# [
#   {{
#     "question": "text",
#     "options": ["A", "B", "C", "D"],
#     "answer": "A"
#   }}
# ]

# SUBJECT: {subject}
# TOPIC: {topic}
# DIFFICULTY: {difficulty}
# """

#     try:
#         response = client.responses.create(
#             model="gpt-4.1-mini",
#             input=prompt
#         )

#         raw = response.output_text
#         quiz = json.loads(raw)
#         return jsonify(quiz)

#     except Exception as e:
#         print("Quiz generation error:", e)
#         return jsonify({"error": "Quiz generation failed"}), 500
@app.route("/generate-quiz", methods=["POST"])
def generate_quiz():
    data = request.json
    subject = data.get("subject")
    topic = data.get("topic")
    difficulty = data.get("difficulty")

    prompt = f"""
Return ONLY valid JSON.
Generate exactly 10 MCQs.

FORMAT:
[
  {{
    "question": "text",
    "options": ["A", "B", "C", "D"],
    "answer": "A"
  }}
]

SUBJECT: {subject}
TOPIC: {topic}
DIFFICULTY: {difficulty}

Strictly return only the JSON array. Do NOT add any extra text.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        raw = response.choices[0].message.content.strip()
        print("🔹 RAW OPENAI TEXT:", raw)

        # Make sure to only keep text between first [ and last ]
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start == -1 or end == -1:
            raise ValueError("No JSON array found in response")

        quiz = json.loads(raw[start:end])
        return jsonify(quiz)

    except Exception as e:
        print("❌ QUIZ ERROR:", e)
        return jsonify({"error": "Quiz generation failed"}), 500




# ---------------- SAVE QUIZ RESULT ----------------
@app.route("/save-result", methods=["POST"])
def save_result():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO quiz_results (subject, topic, score, total, time_taken)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["subject"],
        data["topic"],
        data["score"],
        data["total"],
        data["timeTaken"]
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "saved"})

# ---------------- PRACTICE / TEST TABLE ----------------
@app.route("/practice-data/<subject>")
def practice_data(subject):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT 
            topic,
            ROUND(AVG(score * 100.0 / total), 0) AS avg_score,
            COUNT(*) AS attempts,
            ROUND(AVG(time_taken), 0) AS timeTaken
        FROM quiz_results
        WHERE subject = ?
        GROUP BY topic
    """, (subject,))
    rows = c.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ---------------- WEAKNESS ANALYSIS ----------------
# @app.route("/weakness-data/<subject>")
# def weakness_data(subject):
#     conn = get_db()
#     c = conn.cursor()
#     c.execute("""
#         SELECT topic,
#                SUM(score) AS obtained,
#                SUM(total) AS total
#         FROM quiz_results
#         WHERE subject=?
#         GROUP BY topic
#     """, (subject,))
#     rows = c.fetchall()
#     conn.close()

#     result = {}
#     for r in rows:
#         percent = (r["obtained"] / r["total"]) * 100
#         result[r["topic"]] = round(100 - percent)

#     return jsonify(result)
@app.route("/weakness-data/<subject>")
def weakness_data(subject):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT topic,
               SUM(score) AS obtained,
               SUM(total) AS total
        FROM quiz_results
        WHERE subject=?
        GROUP BY topic
    """, (subject,))
    rows = c.fetchall()
    conn.close()

    result = {}
    for r in rows:
        if r["total"] == 0 or r["total"] is None:
            percent = 0
        else:
            percent = (r["obtained"] / r["total"]) * 100
        result[r["topic"]] = round(100 - percent)

    print("🔹 Weakness Data:", result)  # Debug log
    return jsonify(result)

# ---------------- AI FEEDBACK ----------------
@app.route("/feedback-data/<subject>")
def feedback_data(subject):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT topic,
               AVG(score * 100.0 / total) AS avg_score
        FROM quiz_results
        WHERE subject=?
        GROUP BY topic
    """, (subject,))
    rows = c.fetchall()
    conn.close()

    labels, scores, tips = [], [], []

    for r in rows:
        labels.append(r["topic"])
        scores.append(round(r["avg_score"]))

        if r["avg_score"] < 50:
            tips.append(f"Focus more on {r['topic']}")
        elif r["avg_score"] < 75:
            tips.append(f"Practice {r['topic']} more")
        else:
            tips.append(f"Good job in {r['topic']}")

    return jsonify({
        "labels": labels,
        "scores": scores,
        "tips": tips
    })

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
