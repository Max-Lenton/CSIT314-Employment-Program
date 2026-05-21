import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from extensions import db
from models import Candidate, WorkExperience, Skill, Employer, JobPosting

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///database.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#PDFs will be saved in the static folder
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'resumes')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#limiting to 5MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

#obviously only if it exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def homepage():
    return render_template("homepage.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/signup", methods=["GET"])
def signup_page():
    return render_template("signup.html")

@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.json
    
    account_type = data.get("account_type")
    username = data.get("username")
    password = data.get("password")
    display_name = data.get("display_name")

    if not all([account_type, username, password, display_name]):
        return jsonify({"message": "Please fill in all of the required fields."})
    
    try:
        if account_type == "candidate":
            new_account = Candidate(username=username, password=password, full_name=display_name)
        elif account_type == "employer":
            new_account = Employer(username=username, password=password, company_name=display_name)
        else:
            return jsonify({"message": "Invalid account type."}), 400
        
        db.session.add(new_account)
        db.session.commit()
        return jsonify({"message": "Account successfully created!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Username already exists"})

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/employees")
def browse_employees():
    return render_template("employees.html")


@app.route("/jobs")
def browse_jobs():
    return render_template("jobs.html")

@app.route("/upload_resume", methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"message": "No file uploaded"}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
        
    if file and file.filename and file.filename.endswith('.pdf'):
        filename = secure_filename(str(file.filename))
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        file.save(filepath)
        
        return jsonify({"message": "Resume successfully uploaded!"}), 200
        
    return jsonify({"message": "Invalid file type. Please upload a PDF."}), 400