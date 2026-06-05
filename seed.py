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
            "R", "Java", "JavaScript", "TypeScript", "React", "Node.js",
            "Project Management", "Communication", "Leadership",
            "Lab Operations", "Bioinformatics", "Statistics",
            "AWS", "Docker", "Kubernetes", "DevOps",
            "Cybersecurity", "Networking", "C++", "C#", ".NET",
            "Product Management", "UX Design", "Figma", "Marketing", "Sales",
            "Accounting", "Excel", "Power BI", "Tableau", "Finance",
        ]
        skills = {name: Skill(skill_name=name) for name in skill_names}
        db.session.add_all(skills.values())
        db.session.flush()

        # --- Employers ---
        emp1  = Employer(username="biogen",        password=generate_password_hash("password123"), company_name="BioGen Labs",               contact_info="hr@biogenlabs.com",              membership_type="Premium")
        emp2  = Employer(username="nexuspharma",   password=generate_password_hash("password123"), company_name="Nexus Pharma",              contact_info="careers@nexuspharma.com",        membership_type="Standard")
        emp3  = Employer(username="datacore",      password=generate_password_hash("password123"), company_name="DataCore Sciences",         contact_info="jobs@datacoresci.com",           membership_type="Premium")
        emp4  = Employer(username="skynetcorp",    password=generate_password_hash("password123"), company_name="Skynet Corp",               contact_info="hiring@skynetcorp.io",           membership_type="Premium")
        emp5  = Employer(username="initechhr",     password=generate_password_hash("password123"), company_name="Initech",                   contact_info="tps@initech.com",                membership_type="Standard")
        emp6  = Employer(username="medcorp",       password=generate_password_hash("password123"), company_name="Medical Corporation",       contact_info="research@medical.com",           membership_type="Premium")
        emp7  = Employer(username="goblinworks",   password=generate_password_hash("password123"), company_name="Goblin Works",              contact_info="jobs@goblinworks.dev",           membership_type="Standard")
        emp8  = Employer(username="dbcooper_co",   password=generate_password_hash("password123"), company_name="D.B. Cooper & Associates",  contact_info="contact@dbcooper.biz",           membership_type="Premium")
        emp9  = Employer(username="miskatonic",    password=generate_password_hash("password123"), company_name="Miskatonic University",     contact_info="faculty@miskatonic.edu",         membership_type="Premium")
        emp10 = Employer(username="arkhamasylum",  password=generate_password_hash("password123"), company_name="Arkham Sanitarium",         contact_info="admissions@arkhamsanitarium.org",membership_type="Standard")
        emp11 = Employer(username="innsmouthfish", password=generate_password_hash("password123"), company_name="Innsmouth Fisheries Co.",   contact_info="deep@innsmouthfisheries.com",    membership_type="Standard")
        emp12 = Employer(username="esotericorder", password=generate_password_hash("password123"), company_name="Esoteric Order Bar&Grill",  contact_info="eobg@hotmail.com",               membership_type="Premium")
        db.session.add_all([emp1, emp2, emp3, emp4, emp5, emp6, emp7, emp8, emp9, emp10, emp11, emp12])
        db.session.flush()

        # --- Job Postings ---
        jobs = [
            JobPosting(company_id=emp1.company_id,  job_title="Bioinformatics Analyst",        job_description="Analyse genomic data and develop pipelines for clinical research.",                required_education="BSc Bioinformatics or related",        required_exp=2, work_mode="Hybrid",   job_location="Sydney",       salary_range="$80,000-$95,000",   required_skills=[skills["Python"], skills["Bioinformatics"], skills["SQL"]]),
            JobPosting(company_id=emp2.company_id,  job_title="Lab Operations Coordinator",    job_description="Oversee daily lab operations, procurement, and safety compliance.",                required_education="BSc Life Sciences",                    required_exp=3, work_mode="On-site",  job_location="Melbourne",    salary_range="$70,000-$82,000",   required_skills=[skills["Lab Operations"], skills["Project Management"]]),
            JobPosting(company_id=emp3.company_id,  job_title="Data Engineer",                 job_description="Build and maintain data infrastructure for the science platform.",                 required_education="BSc Computer Science or related",      required_exp=3, work_mode="Remote",   job_location="Remote",       salary_range="$100,000-$120,000", required_skills=[skills["Python"], skills["SQL"], skills["Data Analysis"]]),
            JobPosting(company_id=emp1.company_id,  job_title="Machine Learning Researcher",   job_description="Develop ML models to support drug discovery pipelines.",                           required_education="MSc or PhD Machine Learning / AI",     required_exp=4, work_mode="Hybrid",   job_location="Brisbane",     salary_range="$110,000-$130,000", required_skills=[skills["Machine Learning"], skills["Python"], skills["R"]]),
            JobPosting(company_id=emp4.company_id,  job_title="AI Systems Engineer",           job_description="Design and deploy autonomous AI systems.",                                         required_education="MSc Computer Science or AI",           required_exp=5, work_mode="On-site",  job_location="San Francisco", salary_range="$140,000-$180,000",required_skills=[skills["Machine Learning"], skills["Python"], skills["Docker"], skills["Kubernetes"]]),
            JobPosting(company_id=emp4.company_id,  job_title="DevOps Engineer",               job_description="Maintain CI/CD pipelines and cloud infrastructure at scale.",                      required_education="BSc IT or related",                    required_exp=3, work_mode="Remote",   job_location="Remote",       salary_range="$105,000-$125,000", required_skills=[skills["DevOps"], skills["Docker"], skills["AWS"], skills["Kubernetes"]]),
            JobPosting(company_id=emp5.company_id,  job_title="TPS Report Analyst",            job_description="Process and file TPS reports. Cover sheets mandatory.",                            required_education="Bachelor's in anything",               required_exp=1, work_mode="On-site",  job_location="Austin",       salary_range="$45,000-$55,000",   required_skills=[skills["Excel"], skills["Communication"]]),
            JobPosting(company_id=emp5.company_id,  job_title="Senior Software Developer",     job_description="Build internal tools.",                                                            required_education="BSc Computer Science",                 required_exp=4, work_mode="Hybrid",   job_location="Austin",       salary_range="$90,000-$110,000",  required_skills=[skills["Java"], skills["SQL"], skills["Project Management"]]),
            JobPosting(company_id=emp6.company_id,  job_title="Virologist",                    job_description="Research and development in advanced biological sciences.",                        required_education="PhD Virology or Microbiology",         required_exp=6, work_mode="On-site",  job_location="Raccoon City", salary_range="$120,000-$150,000", required_skills=[skills["Lab Operations"], skills["Bioinformatics"], skills["Statistics"]]),
            JobPosting(company_id=emp6.company_id,  job_title="Security Operations Lead",      job_description="Oversee facility security and incident response.",                                 required_education="BSc Security or Military background",  required_exp=5, work_mode="On-site",  job_location="Raccoon City", salary_range="$95,000-$115,000",  required_skills=[skills["Cybersecurity"], skills["Leadership"], skills["Communication"]]),
            JobPosting(company_id=emp7.company_id,  job_title="Frontend Developer",            job_description="Build slick UIs for our flagship products.",                                       required_education="BSc Computer Science or Design",       required_exp=2, work_mode="Remote",   job_location="Remote",       salary_range="$75,000-$95,000",   required_skills=[skills["JavaScript"], skills["TypeScript"], skills["React"], skills["Figma"]]),
            JobPosting(company_id=emp7.company_id,  job_title="Product Manager",               job_description="Drive roadmap and prioritisation across engineering and design.",                  required_education="Bachelor's in Business or Tech",       required_exp=4, work_mode="Hybrid",   job_location="Melbourne",    salary_range="$100,000-$130,000", required_skills=[skills["Product Management"], skills["Communication"], skills["Leadership"]]),
            JobPosting(company_id=emp8.company_id,  job_title="Logistics Coordinator",         job_description="Manage complex multi-jurisdictional supply chain operations.",                     required_education="Bachelor's in Logistics or Business",  required_exp=3, work_mode="Remote",   job_location="Undisclosed",  salary_range="$85,000-$105,000",  required_skills=[skills["Project Management"], skills["Communication"], skills["Excel"]]),
            JobPosting(company_id=emp8.company_id,  job_title="Financial Analyst",             job_description="Analyse cash flows and manage offshore accounts.",                                 required_education="BSc Finance or Accounting",            required_exp=4, work_mode="Remote",   job_location="Remote",       salary_range="$95,000-$120,000",  required_skills=[skills["Finance"], skills["Accounting"], skills["Excel"], skills["Tableau"]]),
            JobPosting(company_id=emp3.company_id,  job_title="Business Intelligence Analyst", job_description="Turn raw data into actionable insights for leadership teams.",                     required_education="BSc Statistics or Business Analytics", required_exp=2, work_mode="Hybrid",   job_location="Sydney",       salary_range="$80,000-$100,000",  required_skills=[skills["Power BI"], skills["Tableau"], skills["SQL"], skills["Statistics"]]),
            JobPosting(company_id=emp9.company_id,  job_title="Lecturer in Occult Studies",    job_description="Deliver undergraduate lectures inrelated fields",                                  required_education="PhD Ancient History or equivalent",    required_exp=5, work_mode="On-site",  job_location="Arkham, MA",   salary_range="$75,000-$90,000",   required_skills=[skills["Communication"], skills["Leadership"], skills["Statistics"]]),
            JobPosting(company_id=emp9.company_id,  job_title="Research Librarian",            job_description="Catalogue and preserve restricted texts in the Orne Library.",                     required_education="MLIS Library Science",                 required_exp=3, work_mode="On-site",  job_location="Arkham, MA",   salary_range="$60,000-$72,000",   required_skills=[skills["Data Analysis"], skills["Communication"], skills["R"]]),
            JobPosting(company_id=emp9.company_id,  job_title="Quantum Physics Researcher",    job_description="Investigate non-Euclidean geometries and resonance phenomena.",                    required_education="PhD Physics or Mathematics",           required_exp=6, work_mode="On-site",  job_location="Arkham, MA",   salary_range="$100,000-$125,000", required_skills=[skills["Python"], skills["Statistics"], skills["R"], skills["Machine Learning"]]),
            JobPosting(company_id=emp10.company_id, job_title="Clinical Psychologist",         job_description="Provide therapy to patients.",                                                     required_education="PhD Clinical Psychology",              required_exp=4, work_mode="On-site",  job_location="Arkham, MA",   salary_range="$85,000-$105,000",  required_skills=[skills["Communication"], skills["Leadership"], skills["Statistics"]]),
            JobPosting(company_id=emp11.company_id, job_title="Marine Logistics Manager",      job_description="Coordinate deep-sea freight operations. Night shifts required.",                   required_education="BSc Maritime Studies",                 required_exp=4, work_mode="On-site",  job_location="Innsmouth, MA",salary_range="$70,000-$88,000",   required_skills=[skills["Project Management"], skills["Excel"], skills["Communication"]]),
            JobPosting(company_id=emp12.company_id, job_title="Ritual Compliance Officer",     job_description="Ensure all ceremonies adhere to ancient rites and health & safety regulations.",   required_education="Any",                                  required_exp=2, work_mode="On-site",  job_location="Innsmouth, MA",salary_range="$55,000-$70,000",   required_skills=[skills["Communication"], skills["Project Management"], skills["Leadership"]]),
        ]
        db.session.add_all(jobs)

        # --- Demo accounts ---
        demo_candidate = Candidate(username="demo",          password=generate_password_hash("Demo1234!"), full_name="Demo Candidate",  contact_info="demo@careerconnect.com",   education="BSc Computer Science",       major="Software Engineering", years_exp=2,  preferred_mode="Hybrid",  preferred_loc="Sydney",      membership_type="Standard", skills=[skills["Python"], skills["SQL"], skills["Communication"]])
        demo_employer  = Employer( username="demo_employer", password=generate_password_hash("Demo1234!"), company_name="Demo Company", contact_info="hiring@democompany.com",   membership_type="Standard")
        db.session.add_all([demo_candidate, demo_employer])
        db.session.flush()
        db.session.add(JobPosting(company_id=demo_employer.company_id, job_title="Demo Role", job_description="A sample job posting for demonstration purposes.", required_education="Any", required_exp=1, work_mode="Hybrid", job_location="Sydney", salary_range="$60,000-$75,000", required_skills=[skills["Communication"]]))

        # --- Candidates ---
        c1  = Candidate(username="johnsmith",       password=generate_password_hash("password123"), full_name="Dr. John Smith",          contact_info="john.smith@email.com",        education="Doctorate in Bioinformatics", major="Bioinformatics",        years_exp=8,  preferred_mode="Hybrid",   preferred_loc="Sydney",       membership_type="Premium",  skills=[skills["Python"], skills["Bioinformatics"], skills["Machine Learning"], skills["SQL"]])
        c2  = Candidate(username="sarahconnor",     password=generate_password_hash("password123"), full_name="Sarah Connor",            contact_info="sarah.connor@skymail.com",    education="MSc Data Science",            major="Data Science",          years_exp=5,  preferred_mode="Remote",   preferred_loc="Melbourne",    membership_type="Standard", skills=[skills["Python"], skills["Data Analysis"], skills["SQL"], skills["R"]])
        c3  = Candidate(username="ellewoods",       password=generate_password_hash("password123"), full_name="Elle Woods",              contact_info="elle.woods@blondemail.com",   education="BSc Computer Science",        major="Software Engineering",  years_exp=3,  preferred_mode="On-site",  preferred_loc="Brisbane",     membership_type="Standard", skills=[skills["Java"], skills["SQL"], skills["Project Management"]])
        c4  = Candidate(username="patrickbateman",  password=generate_password_hash("password123"), full_name="Patrick Bateman",         contact_info="patrick.bateman@email.com",   education="BSc Life Sciences",           major="Biochemistry",          years_exp=4,  preferred_mode="Hybrid",   preferred_loc="Sydney",       membership_type="Premium",  skills=[skills["Lab Operations"], skills["Communication"], skills["Bioinformatics"]])
        c5  = Candidate(username="dbcooper",        password=generate_password_hash("password123"), full_name="D.B. Cooper",             contact_info="db@gmail.com",                education="No formal qualifications",    major="Self-taught",           years_exp=12, preferred_mode="Remote",   preferred_loc="Undisclosed",  membership_type="Premium",  skills=[skills["Communication"], skills["Leadership"], skills["Project Management"], skills["Finance"]])
        c6  = Candidate(username="waltermitty",     password=generate_password_hash("password123"), full_name="Walter Mitty",            contact_info="walter@life.com",             education="BSc Photography",             major="Photojournalism",       years_exp=6,  preferred_mode="Remote",   preferred_loc="Iceland",      membership_type="Standard", skills=[skills["Communication"], skills["Marketing"], skills["Figma"]])
        c7  = Candidate(username="elliotalderson",  password=generate_password_hash("password123"), full_name="Elliot Alderson",         contact_info="elliot@fsociety.net",         education="BSc Computer Science",        major="Cybersecurity",         years_exp=7,  preferred_mode="Remote",   preferred_loc="New York",     membership_type="Premium",  skills=[skills["Cybersecurity"], skills["Python"], skills["Networking"], skills["C++"]])
        c8  = Candidate(username="lesliknope",      password=generate_password_hash("password123"), full_name="Leslie Knope",            contact_info="lknope@pawneegov.com",        education="BA Political Science",        major="Public Administration", years_exp=10, preferred_mode="On-site",  preferred_loc="Pawnee",       membership_type="Standard", skills=[skills["Project Management"], skills["Leadership"], skills["Communication"], skills["Excel"]])
        c9  = Candidate(username="royKent",         password=generate_password_hash("password123"), full_name="Roy Kent",                contact_info="roy@afcrichmond.com",         education="No formal qualifications",    major="Football",              years_exp=15, preferred_mode="On-site",  preferred_loc="London",       membership_type="Standard", skills=[skills["Leadership"], skills["Communication"]])
        c10 = Candidate(username="jessicafletcher", password=generate_password_hash("password123"), full_name="Jessica Fletcher",        contact_info="j.fletcher@cabotcove.com",    education="MA English Literature",       major="Creative Writing",      years_exp=30, preferred_mode="Remote",   preferred_loc="Cabot Cove",   membership_type="Premium",  skills=[skills["Communication"], skills["Marketing"], skills["Statistics"]])
        c11 = Candidate(username="samcarter",       password=generate_password_hash("password123"), full_name="Dr. Samantha Carter",     contact_info="s.carter@sgc.mil",            education="PhD Astrophysics",            major="Theoretical Physics",   years_exp=12, preferred_mode="On-site",  preferred_loc="Colorado",     membership_type="Premium",  skills=[skills["Python"], skills["Statistics"], skills["Machine Learning"], skills["Data Analysis"], skills["R"]])
        c12 = Candidate(username="randolphcarter",  password=generate_password_hash("password123"), full_name="Randolph Carter",         contact_info="r.carter@dreamlandsmail.net", education="BA Classics & Philosophy",    major="Oneirology",            years_exp=20, preferred_mode="Remote",   preferred_loc="Boston, MA",   membership_type="Premium",  skills=[skills["Communication"], skills["Leadership"], skills["Statistics"], skills["R"]])
        c13 = Candidate(username="herbertwest",     password=generate_password_hash("password123"), full_name="Dr. Herbert West",        contact_info="h.west@miskatonic.edu",       education="MD Miskatonic University",    major="Experimental Medicine", years_exp=9,  preferred_mode="On-site",  preferred_loc="Arkham, MA",   membership_type="Premium",  skills=[skills["Lab Operations"], skills["Bioinformatics"], skills["Python"], skills["Statistics"]])
        c14 = Candidate(username="henryarmitage",   password=generate_password_hash("password123"), full_name="Prof. Henry Armitage",    contact_info="h.armitage@miskatonic.edu",   education="PhD Ancient Languages",       major="Archival Studies",      years_exp=35, preferred_mode="On-site",  preferred_loc="Arkham, MA",   membership_type="Premium",  skills=[skills["Data Analysis"], skills["Communication"], skills["Leadership"], skills["R"]])
        c15 = Candidate(username="cdexter_ward",    password=generate_password_hash("password123"), full_name="Charles Dexter Ward",     contact_info="cdw@wardmansion.com",         education="BSc Chemistry & History",     major="Alchemical Sciences",   years_exp=6,  preferred_mode="On-site",  preferred_loc="Providence, RI",membership_type="Standard", skills=[skills["Lab Operations"], skills["Data Analysis"], skills["Python"], skills["Statistics"]])
        c16 = Candidate(username="npeaslee",        password=generate_password_hash("password123"), full_name="Prof. Nathaniel Peaslee", contact_info="n.peaslee@miskatonic.edu",    education="PhD Political Economy",       major="Economics",             years_exp=25, preferred_mode="Hybrid",   preferred_loc="Arkham, MA",   membership_type="Premium",  skills=[skills["Statistics"], skills["Data Analysis"], skills["R"], skills["Tableau"], skills["Excel"]])
        c17 = Candidate(username="robertblake",     password=generate_password_hash("password123"), full_name="Robert Blake",            contact_info="r.blake@writer.com",          education="BA Fine Arts",                major="Creative Writing",      years_exp=4,  preferred_mode="Remote",   preferred_loc="Providence, RI",membership_type="Standard", skills=[skills["Marketing"], skills["Communication"], skills["Figma"], skills["UX Design"]])
        c18 = Candidate(username="waltergilman",    password=generate_password_hash("password123"), full_name="Walter Gilman",           contact_info="w.gilman@miskatonic.edu",     education="BSc Mathematics & Physics",   major="Non-Euclidean Geometry",years_exp=2,  preferred_mode="On-site",  preferred_loc="Arkham, MA",   membership_type="Standard", skills=[skills["Python"], skills["Statistics"], skills["R"], skills["Machine Learning"]])
        c19 = Candidate(username="crawfordtill",    password=generate_password_hash("password123"), full_name="Crawford Tillinghast",    contact_info="c.tillinghast@resonance.net", education="MSc Electrical Engineering",  major="Resonance Physics",     years_exp=8,  preferred_mode="On-site",  preferred_loc="Providence, RI",membership_type="Premium",  skills=[skills["C++"], skills["Python"], skills["DevOps"], skills["Networking"], skills["Statistics"]])
        c20 = Candidate(username="keziahmason",     password=generate_password_hash("password123"), full_name="Keziah Mason",            contact_info="k.mason@arkham.net",          education="No formal qualifications",    major="Applied Mathematics",   years_exp=300,preferred_mode="Remote",   preferred_loc="Arkham, MA",   membership_type="Premium",  skills=[skills["Statistics"], skills["R"], skills["Machine Learning"], skills["Python"]])
        db.session.add_all([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16, c17, c18, c19, c20])
        db.session.flush()

        db.session.add_all([
            WorkExperience(candidate_id=demo_candidate.candidate_id, job_title="Junior Developer",         company_name="Demo Company",           start_date=date(2024, 1, 1),  end_date=None),
            WorkExperience(candidate_id=c1.candidate_id,   job_title="Senior Researcher",        company_name="BioGen Labs",            start_date=date(2019, 3, 1),  end_date=None),
            WorkExperience(candidate_id=c1.candidate_id,   job_title="Junior Researcher",        company_name="Nexus Pharma",           start_date=date(2016, 6, 1),  end_date=date(2019, 2, 28)),
            WorkExperience(candidate_id=c2.candidate_id,   job_title="Data Analyst",             company_name="DataCore Sciences",      start_date=date(2020, 1, 15), end_date=None),
            WorkExperience(candidate_id=c2.candidate_id,   job_title="Graduate Analyst",         company_name="AusStats",               start_date=date(2018, 3, 1),  end_date=date(2019, 12, 31)),
            WorkExperience(candidate_id=c3.candidate_id,   job_title="Software Developer",       company_name="TechStart Ltd",          start_date=date(2021, 7, 1),  end_date=None),
            WorkExperience(candidate_id=c4.candidate_id,   job_title="Lab Technician",           company_name="Nexus Pharma",           start_date=date(2020, 9, 1),  end_date=date(2022, 8, 31)),
            WorkExperience(candidate_id=c4.candidate_id,   job_title="Research Assistant",       company_name="BioGen Labs",            start_date=date(2022, 9, 1),  end_date=None),
            WorkExperience(candidate_id=c5.candidate_id,   job_title="Independent Consultant",   company_name="Self-Employed",          start_date=date(2012, 1, 1),  end_date=None),
            WorkExperience(candidate_id=c5.candidate_id,   job_title="Regional Manager",         company_name="Northwest Airlines",     start_date=date(2008, 3, 1),  end_date=date(2011, 11, 24)),
            WorkExperience(candidate_id=c6.candidate_id,   job_title="Staff Photographer",       company_name="LIFE Magazine",          start_date=date(2018, 1, 1),  end_date=None),
            WorkExperience(candidate_id=c6.candidate_id,   job_title="Junior Designer",          company_name="Creative Co.",           start_date=date(2016, 5, 1),  end_date=date(2017, 12, 31)),
            WorkExperience(candidate_id=c7.candidate_id,   job_title="Security Engineer",        company_name="Allsafe Cybersecurity",  start_date=date(2019, 6, 1),  end_date=None),
            WorkExperience(candidate_id=c7.candidate_id,   job_title="Freelance Pentester",      company_name="fsociety",               start_date=date(2015, 1, 1),  end_date=date(2019, 5, 31)),
            WorkExperience(candidate_id=c8.candidate_id,   job_title="Deputy Director",          company_name="Pawnee Parks & Rec",     start_date=date(2014, 1, 1),  end_date=None),
            WorkExperience(candidate_id=c9.candidate_id,   job_title="Player",                   company_name="AFC Richmond",           start_date=date(2008, 8, 1),  end_date=date(2022, 5, 31)),
            WorkExperience(candidate_id=c9.candidate_id,   job_title="Assistant Coach",          company_name="AFC Richmond",           start_date=date(2022, 6, 1),  end_date=None),
            WorkExperience(candidate_id=c10.candidate_id,  job_title="Crime Novelist",           company_name="Self-Published",         start_date=date(1994, 1, 1),  end_date=None),
            WorkExperience(candidate_id=c10.candidate_id,  job_title="English Teacher",          company_name="Cabot Cove High",        start_date=date(1985, 9, 1),  end_date=date(1993, 6, 30)),
            WorkExperience(candidate_id=c11.candidate_id,  job_title="Lead Scientist",           company_name="Stargate Command",       start_date=date(2013, 7, 1),  end_date=None),
            WorkExperience(candidate_id=c11.candidate_id,  job_title="Research Fellow",          company_name="MIT Astrophysics Lab",   start_date=date(2010, 1, 1),  end_date=date(2013, 6, 30)),
            WorkExperience(candidate_id=c12.candidate_id,  job_title="Dreamer & Explorer",       company_name="The Dreamlands",         start_date=date(2004, 1, 1),  end_date=None),
            WorkExperience(candidate_id=c12.candidate_id,  job_title="Antiquarian",              company_name="Carter Estate",          start_date=date(1998, 5, 1),  end_date=date(2003, 12, 31)),
            WorkExperience(candidate_id=c13.candidate_id,  job_title="Research Physician",       company_name="Miskatonic University",  start_date=date(2018, 9, 1),  end_date=None),
            WorkExperience(candidate_id=c13.candidate_id,  job_title="Army Surgeon",             company_name="US Army Medical Corps",  start_date=date(2015, 3, 1),  end_date=date(2018, 8, 31)),
            WorkExperience(candidate_id=c14.candidate_id,  job_title="Head Librarian",           company_name="Orne Library, MU",       start_date=date(2000, 9, 1),  end_date=None),
            WorkExperience(candidate_id=c14.candidate_id,  job_title="Associate Professor",      company_name="Miskatonic University",  start_date=date(1990, 9, 1),  end_date=date(2000, 8, 31)),
            WorkExperience(candidate_id=c15.candidate_id,  job_title="Independent Researcher",   company_name="Ward Mansion Laboratory",start_date=date(2019, 1, 1),  end_date=None),
            WorkExperience(candidate_id=c16.candidate_id,  job_title="Professor of Economics",   company_name="Miskatonic University",  start_date=date(2001, 9, 1),  end_date=None),
            WorkExperience(candidate_id=c16.candidate_id,  job_title="Visiting Scholar",         company_name="Yith Central Archives",  start_date=date(1999, 1, 1),  end_date=date(2001, 6, 30)),
            WorkExperience(candidate_id=c17.candidate_id,  job_title="Freelance Writer",         company_name="Self-Employed",          start_date=date(2021, 1, 1),  end_date=None),
            WorkExperience(candidate_id=c17.candidate_id,  job_title="Illustrator",              company_name="Weird Tales Magazine",   start_date=date(2019, 6, 1),  end_date=date(2020, 12, 31)),
            WorkExperience(candidate_id=c18.candidate_id,  job_title="Graduate Researcher",      company_name="Miskatonic University",  start_date=date(2024, 9, 1),  end_date=None),
            WorkExperience(candidate_id=c19.candidate_id,  job_title="Lead Engineer",            company_name="Tillinghast Resonator Lab", start_date=date(2018, 4, 1),end_date=None),
            WorkExperience(candidate_id=c19.candidate_id,  job_title="RF Engineer",              company_name="Providence Telco",       start_date=date(2015, 1, 1),  end_date=date(2018, 3, 31)),
            WorkExperience(candidate_id=c20.candidate_id,  job_title="Independent Mathematician",company_name="N/A",                    start_date=date(1692, 1, 1),  end_date=None),
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

if __name__ == "__main__":
    seed()
