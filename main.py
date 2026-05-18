import os
from flask import Flask, render_template
from extensions import db
from models import Candidate, WorkExperience, Skill, Employer, JobPosting

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///database.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


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