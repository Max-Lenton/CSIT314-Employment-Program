from extensions import db


# Junction table: Candidate <-> Skill
candidate_skill = db.Table(
    "Candidate_Skill",
    db.Column("candidate_id", db.Integer, db.ForeignKey("Candidate.candidate_id"), primary_key=True),
    db.Column("skill_id", db.Integer, db.ForeignKey("Skill.skill_id"), primary_key=True),
)

# Junction table: JobPosting <-> Skill
job_required_skill = db.Table(
    "Job_RequiredSkill",
    db.Column("job_id", db.Integer, db.ForeignKey("JobPosting.job_id"), primary_key=True),
    db.Column("skill_id", db.Integer, db.ForeignKey("Skill.skill_id"), primary_key=True),
)


class Candidate(db.Model):
    __tablename__ = "Candidate"

    candidate_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(200))
    education = db.Column(db.String(100))
    years_exp = db.Column(db.Integer)
    preferred_mode = db.Column(db.String(50))
    preferred_loc = db.Column(db.String(100))
    major = db.Column(db.String(100))
    membership_type = db.Column(db.String(50))
    resume_path = db.Column(db.String(255))

    work_experiences = db.relationship("WorkExperience", backref="candidate", lazy=True)
    skills = db.relationship("Skill", secondary=candidate_skill, backref="candidates")


class WorkExperience(db.Model):
    __tablename__ = "WorkExperience"

    work_exp_id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("Candidate.candidate_id"), nullable=False)
    job_title = db.Column(db.String(100))
    company_name = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)


class Skill(db.Model):
    __tablename__ = "Skill"

    skill_id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(100), nullable=False, unique=True)


class Employer(db.Model):
    __tablename__ = "Employer"

    company_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(200))
    membership_type = db.Column(db.String(50))

    job_postings = db.relationship("JobPosting", backref="employer", lazy=True)


class JobPosting(db.Model):
    __tablename__ = "JobPosting"

    job_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("Employer.company_id"), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text)
    required_education = db.Column(db.String(100))
    required_exp = db.Column(db.Integer)
    work_mode = db.Column(db.String(50))
    job_location = db.Column(db.String(100))
    salary_range = db.Column(db.String(50))

    required_skills = db.relationship("Skill", secondary=job_required_skill, backref="job_postings")


class Application(db.Model):
    __tablename__ = "Application"

    application_id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("Candidate.candidate_id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("JobPosting.job_id"), nullable=False)
    # 'application' = candidate applied, 'offer' = employer offered
    type = db.Column(db.String(20), nullable=False)
    # 'pending', 'accepted', 'rejected'
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    candidate = db.relationship("Candidate", backref="applications")
    job = db.relationship("JobPosting", backref="applications")

