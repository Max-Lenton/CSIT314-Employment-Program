from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def homepage():
    return render_template("homepage.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/employees")
def browse_employees():
    return render_template("employees.html")


@app.route("/jobs")
def browse_jobs():
    return render_template("jobs.html")