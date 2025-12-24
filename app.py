import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
# from openai import OpenAI
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- AI CLIENT ----------------
# client = OpenAI(api_key="sk-proj-Gy3CPBQMeoXSPT1l51-Toh20TZ5iX38E663jXzPlmpjQwkar4hnwTPpTaL7zt5MRbq9qCzBuITT3BlbkFJxyij9Iy52S6rtyG0xLYvzHm86eGSdzjw0rxy5uZPUVzGUxi_8rFaJk6B5GE2sPbftf1Jg_cDkAsk-proj-Gy3CPBQMeoXSPT1l51-Toh20TZ5iX38E663jXzPlmpjQwkar4hnwTPpTaL7zt5MRbq9qCzBuITT3BlbkFJxyij9Iy52S6rtyG0xLYvzHm86eGSdzjw0rxy5uZPUVzGUxi_8rFaJk6B5GE2sPbftf1Jg_cDkA")

# ---------------- LOGIN (UNCHANGED) ----------------
TEACHERS = {
    "teacher": "teacher123",
    "admin": "admin123"
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in TEACHERS and TEACHERS[username] == password:
            session["teacher"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid Login")

    return render_template("login.html")

# ---------------- DASHBOARD (UNCHANGED) ----------------
@app.route("/dashboard")
def dashboard():
    if "teacher" not in session:
        return redirect(url_for("login"))

    return render_template("studentindex.html")

# ---------------- QUIZ PAGE (UNCHANGED) ----------------
@app.route("/quiz")
@app.route("/quiz")
def quiz():
    subject = request.args.get("subject")
    return render_template("quiz.html", subject=subject)


# ---------------- AI QUESTION GENERATION (ADDED) ------------
@app.route("/generate-quiz", methods=["POST"])
def generate_quiz():
    data = request.json

    subject = data.get("subject")
    topic = data.get("topic")
    difficulty = data.get("difficulty")

    prompt = f"""
Generate exactly 10 {difficulty} level MCQs for subject {subject} on topic {topic}.

Rules:
- Each question must have 4 options
- Only ONE correct answer
- Return ONLY valid JSON
- No explanation
- No markdown
- No extra text

JSON format:
[
  {{
    "question": "Question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Option A"
  }}
]
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        quiz_text = response.choices[0].message.content.strip()
        quiz_data = json.loads(quiz_text)

        return jsonify(quiz_data)

    except Exception as e:
        print("AI ERROR:", e)
        return jsonify({"error": "AI generation failed"}), 500

# ---------------- LOGOUT (UNCHANGED) ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
