import json
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import os
import json
import openai

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.secret_key = "secret123"

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

init_db()

# ---------------- LOGIN ----------------
TEACHERS = {
    "teacher": "teacher123",
    "admin": "admin123"
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if TEACHERS.get(request.form["username"]) == request.form["password"]:
            session["student_id"] = "student1"  # mock student
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid Login")
    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "student_id" not in session:
        return redirect(url_for("login"))
    return render_template("studentindex.html")

# ---------------- QUIZ ----------------
@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

# ---------------- AI QUIZ GENERATION ----------------
@app.route("/generate-quiz", methods=["POST"])
def generate_quiz():
    data = request.json
    subject = data.get("subject")
    topic = data.get("topic")
    difficulty = data.get("difficulty")

    prompt = f"""
You are an API.

Return ONLY valid JSON.
Do NOT explain.
Do NOT use markdown.

Generate exactly 10 MCQ questions.

FORMAT:
[
  {{
    "question": "Question text",
    "options": ["A", "B", "C", "D"],
    "answer": "A"
  }}
]

SUBJECT: {subject}
TOPIC: {topic}
DIFFICULTY: {difficulty}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        raw = response.choices[0].message.content.strip()
        print("🔥 RAW AI RESPONSE:", raw)

        # 🛡️ Extract JSON safely
        start = raw.find("[")
        end = raw.rfind("]") + 1
        json_text = raw[start:end]

        quiz = json.loads(json_text)

        if not isinstance(quiz, list):
            raise ValueError("Quiz is not a list")

        return jsonify(quiz)

    except Exception as e:
        print("❌ QUIZ GENERATION FAILED:", e)

        # ✅ FALLBACK QUESTIONS (SO UI NEVER BREAKS)
        return jsonify([
            {
                "question": "What is an array?",
                "options": [
                    "Collection of elements",
                    "Single variable",
                    "Function",
                    "Pointer"
                ],
                "answer": "Collection of elements"
            }
        ])


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

# ---------------- PRACTICE DATA ----------------
@app.route("/practice-data/<subject>")
def practice_data(subject):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT topic,
               ROUND(AVG(score * 100.0 / total), 0) AS avg_score,
               COUNT(*) AS attempts
        FROM quiz_results
        WHERE subject=?
        GROUP BY topic
    """, (subject,))
    rows = c.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ---------------- WEAKNESS ANALYSIS ----------------
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
        percent = (r["obtained"] / r["total"]) * 100
        result[r["topic"]] = round(100 - percent)

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
    app.run(debug=True)
