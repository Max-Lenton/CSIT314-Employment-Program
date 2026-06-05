import os
import difflib
from flask import Flask, render_template, request, jsonify, session, redirect
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import Candidate, WorkExperience, Skill, Employer, JobPosting

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///database.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

UPLOAD_FOLDER = os.path.join("static", "uploads", "resumes")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)

with app.app_context():
    db.create_all()


# Helpers

def fuzzy_match(query, text, threshold=0.6):
    """Return True if query fuzzy-matches anywhere in text (case-insensitive)."""
    if not query or not text:
        return False
    q = query.lower()
    t = text.lower()
    if q in t:
        return True
    # Check word-level similarity using difflib
    ratio = difflib.SequenceMatcher(None, q, t).ratio()
    if ratio >= threshold:
        return True
    # Also check each word in text
    for word in t.split():
        r = difflib.SequenceMatcher(None, q, word).ratio()
        if r >= threshold:
            return True
    return False


def job_to_dict(j):
    return {
        "id": j.job_id,
        "title": j.job_title,
        "company": j.employer.company_name if j.employer else "",
        "description": j.job_description,
        "location": j.job_location,
        "work_mode": j.work_mode,
        "salary_range": j.salary_range,
        "required_exp": j.required_exp,
        "required_education": j.required_education,
        "required_skills": [s.skill_name for s in j.required_skills],
    }


def candidate_to_dict(c):
    return {
        "id": c.candidate_id,
        "name": c.full_name,
        "education": c.education,
        "major": c.major,
        "years_exp": c.years_exp,
        "preferred_mode": c.preferred_mode,
        "preferred_loc": c.preferred_loc,
        "membership_type": c.membership_type,
        "skills": [s.skill_name for s in c.skills],
        "work_experience": [
            {"job_title": w.job_title, "company_name": w.company_name}
            for w in c.work_experiences
        ],
    }


# Session validation

@app.before_request
def validate_session():
    if "user_id" not in session:
        return
    account_type = session.get("account_type")
    if account_type == "candidate":
        if not Candidate.query.get(session["user_id"]):
            session.clear()
    elif account_type == "employer":
        if not Employer.query.get(session["user_id"]):
            session.clear()
    else:
        session.clear()


# Page routes

@app.route("/")
def homepage():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("homepage.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login")

    user_name = session.get("name", "Unknown User")
    initials = "".join([p[0].upper() for p in user_name.split() if p])[:2]
    account_type = session.get("account_type")

    if account_type == "candidate":
        candidate_data = Candidate.query.get(session["user_id"])
        all_skills = Skill.query.order_by(Skill.skill_name).all()
        return render_template("candidate_profile.html",
                               user_name=user_name, initials=initials,
                               candidate=candidate_data,
                               all_skills=all_skills)

    if account_type == "employer":
        employer_data = Employer.query.get(session["user_id"])
        all_skills = Skill.query.order_by(Skill.skill_name).all()
        return render_template("employer_profile.html",
                               user_name=user_name, initials=initials,
                               employer=employer_data,
                               all_skills=all_skills)

    session.clear()
    return redirect("/login")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup_page():
    return render_template("signup.html")


@app.route("/employees")
def browse_employees():
    return render_template("employees.html", account_type=session.get("account_type", ""))

@app.route("/candidate/<int:candidate_id>")
def view_candidate(candidate_id):
    candidate_data = Candidate.query.get_or_404(candidate_id)

    user_name = session.get("name", "Guest")
    initials = "".join([p[0].upper() for p in user_name.split() if p])[:2] if user_name != "Guest" else "??"

    return render_template(
        "candidate_readonly.html",
        candidate=candidate_data,
        user_name=user_name,
        initials=initials,
        account_type=session.get("account_type", "")
    )


@app.route("/jobs")
def browse_jobs():
    return render_template("jobs.html", account_type=session.get("account_type", ""))

@app.route("/job/<int:job_id>")
def view_job(job_id):
    job_data = JobPosting.query.get_or_404(job_id)
    
    user_name = session.get("name", "Guest")
    initials = "".join([p[0].upper() for p in user_name.split() if p])[:2] if user_name != "Guest" else "??"

    return render_template(
        "job_readonly.html",
        job=job_data,
        user_name=user_name,
        initials=initials,
        account_type=session.get("account_type", "")
    )


# Auth API

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"message": "Username and password are required."}), 400

    candidate = Candidate.query.filter_by(username=username).first()
    if candidate and check_password_hash(candidate.password, password):
        session["user_id"] = candidate.candidate_id
        session["account_type"] = "candidate"
        session["name"] = candidate.full_name
        return jsonify({"message": "Login successful!"}), 200

    employer = Employer.query.filter_by(username=username).first()
    if employer and check_password_hash(employer.password, password):
        session["user_id"] = employer.company_id
        session["account_type"] = "employer"
        session["name"] = employer.company_name
        return jsonify({"message": "Login successful!"}), 200

    return jsonify({"message": "Invalid username or password."}), 401


@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.json or {}
    account_type = data.get("account_type")
    username = data.get("username", "").strip()
    password = data.get("password", "")
    display_name = data.get("display_name", "").strip()

    if not all([account_type, username, password, display_name]):
        return jsonify({"message": "Please fill in all required fields."}), 400

    hashed = generate_password_hash(password)

    try:
        if account_type == "candidate":
            new_account = Candidate(username=username, password=hashed, full_name=display_name)
        elif account_type == "employer":
            new_account = Employer(username=username, password=hashed, company_name=display_name)
        else:
            return jsonify({"message": "Invalid account type."}), 400

        db.session.add(new_account)
        db.session.commit()
        return jsonify({"message": "Account created successfully!"}), 201

    except Exception:
        db.session.rollback()
        return jsonify({"message": "Username already exists."}), 409


# Candidate profile API

@app.route("/api/update_profile", methods=["POST"])
def update_profile():
    if "user_id" not in session or session.get("account_type") != "candidate":
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json or {}
    candidate = Candidate.query.get(session["user_id"])
    if not candidate:
        return jsonify({"message": "Candidate not found."}), 404

    candidate.education = data.get("education", candidate.education)
    candidate.major = data.get("major", candidate.major)
    candidate.contact_info = data.get("contact_info", candidate.contact_info)
    if data.get("years_exp") is not None:
        candidate.years_exp = data.get("years_exp")
    candidate.preferred_mode = data.get("preferred_mode", candidate.preferred_mode)
    candidate.preferred_loc = data.get("preferred_loc", candidate.preferred_loc)
    db.session.commit()
    return jsonify({"message": "Profile saved successfully!"}), 200


@app.route("/api/update_skills", methods=["POST"])
def update_skills():
    if "user_id" not in session or session.get("account_type") != "candidate":
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json or {}
    skill_names = data.get("skills", [])
    candidate = Candidate.query.get(session["user_id"])
    if not candidate:
        return jsonify({"message": "Candidate not found."}), 404

    new_skills = []
    for name in skill_names:
        name = name.strip()
        if not name:
            continue
        skill = Skill.query.filter_by(skill_name=name).first()
        if not skill:
            skill = Skill(skill_name=name)
            db.session.add(skill)
            db.session.flush()
        new_skills.append(skill)

    candidate.skills = new_skills
    db.session.commit()
    return jsonify({"message": "Skills updated!", "skills": [s.skill_name for s in candidate.skills]}), 200


@app.route("/api/work_experience", methods=["POST"])
def add_work_experience():
    if "user_id" not in session or session.get("account_type") != "candidate":
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json or {}
    job_title = data.get("job_title", "").strip()
    company_name = data.get("company_name", "").strip()
    if not job_title or not company_name:
        return jsonify({"message": "Job title and company are required."}), 400

    we = WorkExperience(
        candidate_id=session["user_id"],
        job_title=job_title,
        company_name=company_name,
    )
    db.session.add(we)
    db.session.commit()
    return jsonify({"message": "Work experience added!", "id": we.work_exp_id}), 201


@app.route("/api/work_experience/<int:exp_id>", methods=["DELETE"])
def delete_work_experience(exp_id):
    if "user_id" not in session or session.get("account_type") != "candidate":
        return jsonify({"message": "Unauthorized"}), 401

    we = WorkExperience.query.get(exp_id)
    if not we or we.candidate_id != session["user_id"]:
        return jsonify({"message": "Not found."}), 404

    db.session.delete(we)
    db.session.commit()
    return jsonify({"message": "Deleted."}), 200


@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    if "user_id" not in session or session.get("account_type") != "candidate":
        return jsonify({"message": "Unauthorized"}), 401

    if "resume" not in request.files:
        return jsonify({"message": "No file uploaded."}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"message": "No file selected."}), 400

    if file and file.filename.lower().endswith(".pdf"):
        filename = secure_filename(f"{session['user_id']}_{file.filename}")
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        candidate = Candidate.query.get(session["user_id"])
        if candidate:
            candidate.resume_path = filepath
            db.session.commit()

        return jsonify({"message": "Resume uploaded successfully!"}), 200

    return jsonify({"message": "Invalid file type. Please upload a PDF."}), 400


# Employer job API

@app.route("/api/jobs/create", methods=["POST"])
def create_job():
    if "user_id" not in session or session.get("account_type") != "employer":
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json or {}
    job_title = data.get("job_title", "").strip()
    if not job_title:
        return jsonify({"message": "Job title is required."}), 400

    skill_names = data.get("required_skills", [])
    skills = []
    for name in skill_names:
        name = name.strip()
        if not name:
            continue
        skill = Skill.query.filter_by(skill_name=name).first()
        if not skill:
            skill = Skill(skill_name=name)
            db.session.add(skill)
            db.session.flush()
        skills.append(skill)

    job = JobPosting(
        company_id=session["user_id"],
        job_title=job_title,
        job_description=data.get("job_description", ""),
        required_education=data.get("required_education", ""),
        required_exp=data.get("required_exp"),
        work_mode=data.get("work_mode", ""),
        job_location=data.get("job_location", ""),
        salary_range=data.get("salary_range", ""),
        required_skills=skills,
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({"message": "Job posted successfully!", "id": job.job_id}), 201


@app.route("/api/jobs/<int:job_id>", methods=["DELETE"])
def delete_job(job_id):
    if "user_id" not in session or session.get("account_type") != "employer":
        return jsonify({"message": "Unauthorized"}), 401

    job = JobPosting.query.get(job_id)
    if not job or job.company_id != session["user_id"]:
        return jsonify({"message": "Not found."}), 404

    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job deleted."}), 200


# Membership API

@app.route("/api/upgrade_membership", methods=["POST"])
def upgrade_membership():
    if "user_id" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    account_type = session.get("account_type")
    if account_type == "candidate":
        entity = Candidate.query.get(session["user_id"])
    elif account_type == "employer":
        entity = Employer.query.get(session["user_id"])
    else:
        return jsonify({"message": "Invalid account type."}), 400

    if not entity:
        return jsonify({"message": "Account not found."}), 404

    entity.membership_type = "Premium"
    db.session.commit()
    return jsonify({"message": "Membership upgraded to Premium!"}), 200

# Another membership API (for the tmeplate page)
@app.route("/membership")
def mempership_page():
    if "user_id" not in session:
        return redirect("/login")
    
    return render_template("membership.html", account_type=session.get("account_type", ""))


# Data API

@app.route("/api/candidates")
def api_candidates():
    keyword = request.args.get("keyword", "").strip()
    skill_filter = request.args.get("skill", "").strip()
    min_exp = request.args.get("min_exp", type=int)
    work_mode = request.args.get("work_mode", "").strip()
    education_filter = request.args.get("education", "").strip()

    candidates = Candidate.query.all()
    results = []
    for c in candidates:
        # Skill filter (exact, case-insensitive)
        if skill_filter:
            candidate_skills = [s.skill_name.lower() for s in c.skills]
            if skill_filter.lower() not in candidate_skills:
                continue

        # Min experience filter
        if min_exp is not None and (c.years_exp is None or c.years_exp < min_exp):
            continue

        # Work mode filter
        if work_mode and c.preferred_mode and c.preferred_mode.lower() != work_mode.lower():
            continue

        # Education keyword filter
        if education_filter:
            edu_text = (c.education or "") + " " + (c.major or "")
            if not fuzzy_match(education_filter, edu_text):
                continue

        # Keyword search (name, education, major, skills, work exp)
        if keyword:
            searchable = " ".join([
                c.full_name or "",
                c.education or "",
                c.major or "",
                " ".join(s.skill_name for s in c.skills),
                " ".join((w.job_title or "") + " " + (w.company_name or "") for w in c.work_experiences),
            ])
            if not fuzzy_match(keyword, searchable):
                continue

        results.append(candidate_to_dict(c))

    return jsonify(results)


@app.route("/api/jobs")
def api_jobs():
    keyword = request.args.get("keyword", "").strip()
    work_mode = request.args.get("work_mode", "").strip()
    location = request.args.get("location", "").strip()
    max_exp = request.args.get("max_exp", type=int)

    jobs = JobPosting.query.all()
    results = []
    for j in jobs:
        if work_mode and j.work_mode and j.work_mode.lower() != work_mode.lower():
            continue
        if location and not fuzzy_match(location, j.job_location or ""):
            continue
        if max_exp is not None and j.required_exp is not None and j.required_exp > max_exp:
            continue
        if keyword:
            searchable = " ".join([
                j.job_title or "",
                j.job_description or "",
                j.job_location or "",
                j.required_education or "",
                " ".join(s.skill_name for s in j.required_skills),
            ])
            if not fuzzy_match(keyword, searchable):
                continue
        results.append(job_to_dict(j))

    return jsonify(results)


# Recommendation API

@app.route("/api/recommendations/jobs")
def recommend_jobs():
    """Top job recommendations for the logged-in candidate."""
    if "user_id" not in session or session.get("account_type") != "candidate":
        return jsonify({"message": "Unauthorized"}), 401

    candidate = Candidate.query.get(session["user_id"])
    if not candidate:
        return jsonify({"message": "Not found."}), 404

    candidate_skills = {s.skill_name.lower() for s in candidate.skills}
    jobs = JobPosting.query.all()
    scored = []
    for j in jobs:
        score = 0
        job_skills = {s.skill_name.lower() for s in j.required_skills}

        # Skill overlap (most important, up to 5 points)
        if candidate_skills and job_skills:
            overlap = len(candidate_skills & job_skills) / max(len(job_skills), 1)
            score += overlap * 5

        # Work mode match (1 point)
        if candidate.preferred_mode and j.work_mode:
            if candidate.preferred_mode.lower() == j.work_mode.lower():
                score += 1

        # Experience match (1 point — candidate has enough but not way over)
        if candidate.years_exp is not None and j.required_exp is not None:
            if candidate.years_exp >= j.required_exp:
                score += 1

        # Education keyword match (1 point)
        if candidate.education and j.required_education:
            if fuzzy_match(candidate.education, j.required_education, threshold=0.5):
                score += 1

        scored.append((score, j))

    scored.sort(key=lambda x: x[0], reverse=True)

    is_premium = (candidate.membership_type or "").lower() == "premium"
    limit = None if is_premium else 10
    top = scored[:limit]

    return jsonify([job_to_dict(j) for _, j in top])


@app.route("/api/recommendations/candidates")
def recommend_candidates():
    """Top candidate recommendations for the logged-in employer, optionally for a specific job."""
    if "user_id" not in session or session.get("account_type") != "employer":
        return jsonify({"message": "Unauthorized"}), 401

    job_id = request.args.get("job_id", type=int)
    employer = Employer.query.get(session["user_id"])
    if not employer:
        return jsonify({"message": "Not found."}), 404

    # Use specified job or first job posting
    job = None
    if job_id:
        job = JobPosting.query.get(job_id)
        if job and job.company_id != session["user_id"]:
            job = None
    if not job and employer.job_postings:
        job = employer.job_postings[0]

    if not job:
        return jsonify([])

    required_skills = {s.skill_name.lower() for s in job.required_skills}
    candidates = Candidate.query.all()
    scored = []
    for c in candidates:
        score = 0
        cand_skills = {s.skill_name.lower() for s in c.skills}

        # Skill overlap (up to 5 points)
        if required_skills and cand_skills:
            overlap = len(cand_skills & required_skills) / max(len(required_skills), 1)
            score += overlap * 5

        # Experience match (1 point)
        if c.years_exp is not None and job.required_exp is not None:
            if c.years_exp >= job.required_exp:
                score += 1

        # Work mode match (1 point)
        if c.preferred_mode and job.work_mode:
            if c.preferred_mode.lower() == job.work_mode.lower():
                score += 1

        # Education match (1 point)
        if c.education and job.required_education:
            if fuzzy_match(c.education, job.required_education, threshold=0.5):
                score += 1

        scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)

    is_premium = (employer.membership_type or "").lower() == "premium"
    limit = None if is_premium else 10
    top = scored[:limit]

    return jsonify([candidate_to_dict(c) for _, c in top])
