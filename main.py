import os
from flask import Flask, render_template, request, jsonify, session, redirect
from werkzeug.utils import secure_filename
from extensions import db
from models import Candidate, WorkExperience, Skill, Employer, JobPosting

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///database.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SECRET_KEY"] = "secret_key"

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
    
    candidates_to_add = [
        {"user": "cand1", "pass": "password123", "name": "Alice Smith", "email": "alice@email.com", "edu": "PhD in Bioinformatics", "exp": 5},
        {"user": "cand2", "pass": "password123", "name": "Bob Jones", "email": "bob.j@email.com", "edu": "MSc in Data Science", "exp": 3},
        {"user": "cand3", "pass": "password123", "name": "Charlie Davis", "email": "charlie.d@email.com", "edu": "BSc in Computer Science", "exp": 1}
    ]

    employers_to_add = [
        {"user": "emp1", "pass": "password123", "company": "Aperture Science", "email": "hr@aperture.com"},
        {"user": "emp2", "pass": "password123", "company": "Black Mesa Research", "email": "recruiting@blackmesa.com"},
        {"user": "emp3", "pass": "password123", "company": "Wayne Enterprises", "email": "careers@wayne.com"}
    ]

    for c in candidates_to_add:
        if not Candidate.query.filter_by(username=c["user"]).first():
            new_cand = Candidate(
                username=c["user"],
                password=c["pass"],
                full_name=c["name"],
                contact_info=c["email"],
                education=c["edu"],
                years_exp=c["exp"]
            )
            db.session.add(new_cand)

    for e in employers_to_add:
        if not Employer.query.filter_by(username=e["user"]).first():
            new_emp = Employer(
                username=e["user"],
                password=e["pass"],
                company_name=e["company"],
                contact_info=e["email"]
            )
            db.session.add(new_emp)
            
    db.session.commit()



@app.route("/")
def homepage():
    return render_template("homepage.html")


@app.route("/profile")
def profile():
    if 'user_id' not in session:
        return redirect("/login")
    
    user_name = session.get('name', 'Unknown User')
    initials = "".join([part[0].upper() for part in user_name.split() if part])[:2]
    
    return render_template("profile.html", user_name=user_name, initials=initials)

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

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required."}), 400
    
    candidate = Candidate.query.filter_by(username=username).first()
    if candidate and candidate.password==password:
        session['user_id'] = candidate.candidate_id
        session['account_type'] = 'candidate'
        session['name'] = candidate.full_name
        return jsonify({"message": "Login successful!"}), 200
    
    employer = Employer.query.filter_by(username=username).first()
    if employer and employer.password==password:
        session['user_id'] = employer.employer_id
        session['account_type'] = 'employer'
        session['name'] = employer.full_name
        return jsonify({"message": "Login successful!"}), 200
    
    return jsonify({"message": "Invalid username or password."}), 401

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