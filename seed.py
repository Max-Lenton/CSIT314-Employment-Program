"""
seed.py -- Clears the database and populates it with example data.
Run with: python seed.py
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))

from main import app
from extensions import db
from models import Candidate, WorkExperience, Skill, Employer, JobPosting
from werkzeug.security import generate_password_hash


def seed():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Recreating tables...")
        db.create_all()

        skill_names = [
            "Python", "SQL", "Data Analysis", "Machine Learning",
            "R", "Java", "Project Management", "Communication",
            "Lab Operations", "Bioinformatics",
        ]
        skills = {name: Skill(skill_name=name) for name in skill_names}
        db.session.add_all(skills.values())

        emp1 = Employer(username="biogen",      password=generate_password_hash("password123"), company_name="BioGen Labs",      contact_info="hr@biogenlabs.com",        membership_type="Premium")
        emp2 = Employer(username="nexuspharma", password=generate_password_hash("password123"), company_name="Nexus Pharma",     contact_info="careers@nexuspharma.com",  membership_type="Standard")
        emp3 = Employer(username="datacore",    password=generate_password_hash("password123"), company_name="DataCore Sciences", contact_info="jobs@datacoresci.com",      membership_type="Premium")
        db.session.add_all([emp1, emp2, emp3])
        db.session.flush()

        j1 = JobPosting(company_id=emp1.company_id, job_title="Bioinformatics Analyst",     job_description="Analyse genomic data and develop pipelines for clinical research.", required_education="BSc Bioinformatics or related", required_exp=2, work_mode="Hybrid",   job_location="Sydney",     salary_range="$80,000-$95,000",  required_skills=[skills["Python"], skills["Bioinformatics"], skills["SQL"]])
        j2 = JobPosting(company_id=emp2.company_id, job_title="Lab Operations Coordinator", job_description="Oversee daily lab operations, procurement, and safety compliance.",  required_education="BSc Life Sciences",            required_exp=3, work_mode="On-site",  job_location="Melbourne", salary_range="$70,000-$82,000",  required_skills=[skills["Lab Operations"], skills["Project Management"]])
        j3 = JobPosting(company_id=emp3.company_id, job_title="Data Engineer",              job_description="Build and maintain data infrastructure for the science platform.",    required_education="BSc Computer Science or related", required_exp=3, work_mode="Remote", job_location="Remote",    salary_range="$100,000-$120,000", required_skills=[skills["Python"], skills["SQL"], skills["Data Analysis"]])
        j4 = JobPosting(company_id=emp1.company_id, job_title="Machine Learning Researcher",job_description="Develop ML models to support drug discovery pipelines.",              required_education="MSc or PhD Machine Learning / AI",required_exp=4, work_mode="Hybrid",   job_location="Brisbane",   salary_range="$110,000-$130,000", required_skills=[skills["Machine Learning"], skills["Python"], skills["R"]])
        db.session.add_all([j1, j2, j3, j4])

        # Demo accounts
        demo_candidate = Candidate(username="demo",         password=generate_password_hash("Demo1234!"), full_name="Demo Candidate",  contact_info="demo@coolcats.com",       education="BSc Computer Science",        major="Software Engineering",  years_exp=2, preferred_mode="Hybrid",   preferred_loc="Sydney",         membership_type="Standard",  skills=[skills["Python"], skills["SQL"], skills["Communication"]])
        demo_employer  = Employer( username="demo_employer", password=generate_password_hash("Demo1234!"), company_name="Demo Company", contact_info="hiring@democompany.com",   membership_type="Standard")
        db.session.add_all([demo_candidate, demo_employer])
        db.session.flush()
        db.session.add(JobPosting(company_id=demo_employer.company_id, job_title="Demo Role", job_description="A sample job posting for demonstration purposes.", required_education="Any", required_exp=1, work_mode="Hybrid", job_location="Sydney", salary_range="$60,000-$75,000", required_skills=[skills["Communication"]]))

        c1 = Candidate(username="johnsmith",   password=generate_password_hash("password123"), full_name="Dr. John Smith", contact_info="john.smith@email.com",    education="Doctorate in Bioinformatics", major="Bioinformatics",      years_exp=8, preferred_mode="Hybrid",   preferred_loc="Sydney",    membership_type="Premium",   skills=[skills["Python"], skills["Bioinformatics"], skills["Machine Learning"], skills["SQL"]])
        c2 = Candidate(username="sarahconnor", password=generate_password_hash("password123"), full_name="Sarah Connor",   contact_info="sarah.connor@email.com",  education="MSc Data Science",            major="Data Science",        years_exp=5, preferred_mode="Remote",   preferred_loc="Melbourne", membership_type="Standard",  skills=[skills["Python"], skills["Data Analysis"], skills["SQL"], skills["R"]])
        c3 = Candidate(username="ellewoods",    password=generate_password_hash("password123"), full_name="Elle Woods",      contact_info="elle.woods@email.com",    education="BSc Computer Science",        major="Software Engineering", years_exp=3, preferred_mode="On-site",  preferred_loc="Brisbane",  membership_type="Standard",  skills=[skills["Java"], skills["SQL"], skills["Project Management"]])
        c4 = Candidate(username="patrickbateman", password=generate_password_hash("password123"), full_name="Patrick Bateman", contact_info="patrick.bateman@email.com", education="BSc Life Sciences",           major="Biochemistry",        years_exp=4, preferred_mode="Hybrid",   preferred_loc="Sydney",    membership_type="Premium",   skills=[skills["Lab Operations"], skills["Communication"], skills["Bioinformatics"]])
        db.session.add_all([c1, c2, c3, c4])
        db.session.flush()

        db.session.add_all([
            WorkExperience(candidate_id=demo_candidate.candidate_id, job_title="Junior Developer",  company_name="Demo Company",     start_date=date(2024, 1, 1),  end_date=None),
            WorkExperience(candidate_id=c1.candidate_id, job_title="Senior Researcher",  company_name="BioGen Labs",      start_date=date(2019, 3, 1),  end_date=None),
            WorkExperience(candidate_id=c1.candidate_id, job_title="Junior Researcher",  company_name="Nexus Pharma",     start_date=date(2016, 6, 1),  end_date=date(2019, 2, 28)),
            WorkExperience(candidate_id=c2.candidate_id, job_title="Data Analyst",       company_name="DataCore Sciences",start_date=date(2020, 1, 15), end_date=None),
            WorkExperience(candidate_id=c3.candidate_id, job_title="Software Developer", company_name="TechStart Ltd",    start_date=date(2021, 7, 1),  end_date=None),
            WorkExperience(candidate_id=c4.candidate_id, job_title="Lab Technician",     company_name="Nexus Pharma",     start_date=date(2020, 9, 1),  end_date=date(2022, 8, 31)),
        ])

        db.session.commit() 
        print("Database seeded successfully.")
        print(f"  {Skill.query.count()} skills")
        print(f"  {Employer.query.count()} employers")
        print(f"  {JobPosting.query.count()} job postings")
        print(f"  {Candidate.query.count()} candidates")
        print(f"  {WorkExperience.query.count()} work experiences")
        print()
        print("Demo accounts (password: Demo1234!)")
        print("  Candidate: demo")
        print("  Employer:  demo_employer")
        print()
        print("Other logins (password: password123)")
        print("  Candidates: johnsmith, sarahconnor, ellewoods, patrickbateman")
        print("  Employers:  biogen, nexuspharma, datacore")


if __name__ == "__main__":
    seed()
