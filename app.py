from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret123"

# Teacher credentials
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

@app.route("/dashboard")
def dashboard():
    if "teacher" not in session:
        return redirect(url_for("login"))

    return render_template("teacher_dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
