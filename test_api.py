"""
Unit tests for Career Connect API
Run with:  python -m pytest test_api.py -v
       or: python -m unittest test_api -v

conftest.py must be present — it sets DATABASE_URL to a temp file before
main.py is imported, so all tests run against an isolated database.
"""

import unittest
from main import app
from extensions import db
from models import Candidate, Employer, JobPosting, Skill, Application, WorkExperience
from werkzeug.security import generate_password_hash


class BaseTestCase(unittest.TestCase):
    """Drop and recreate all tables before each test for full isolation."""

    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret"
        self.client = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()
            self._seed()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()


    # Seed helpers


    def _seed(self):
        """Insert one candidate, one employer, and one job posting."""
        candidate = Candidate(
            username="testcandidate",
            password=generate_password_hash("pass123"),
            full_name="Test Candidate",
            education="Bachelor's",
            major="Computer Science",
            years_exp=2,
            preferred_mode="Remote",
            preferred_loc="Sydney",
            membership_type="free",
        )
        employer = Employer(
            username="testemployer",
            password=generate_password_hash("pass456"),
            company_name="Test Corp",
            membership_type="free",
        )
        db.session.add_all([candidate, employer])
        db.session.flush()

        skill_py = Skill(skill_name="Python")
        skill_sql = Skill(skill_name="SQL")
        db.session.add_all([skill_py, skill_sql])
        db.session.flush()

        candidate.skills.append(skill_py)

        job = JobPosting(
            company_id=employer.company_id,
            job_title="Backend Developer",
            job_description="Build APIs.",
            work_mode="Remote",
            job_location="Sydney",
            required_exp=2,
            salary_range="$80,000",
            required_skills=[skill_py, skill_sql],
        )
        db.session.add(job)
        db.session.commit()

    def _login_candidate(self):
        return self.client.post("/api/login", json={
            "username": "testcandidate",
            "password": "pass123",
        })

    def _login_employer(self):
        return self.client.post("/api/login", json={
            "username": "testemployer",
            "password": "pass456",
        })



# 1. Authentication Tests


class TestAuth(BaseTestCase):

    def test_login_candidate_success(self):
        rv = self._login_candidate()
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b"Login successful", rv.data)

    def test_login_employer_success(self):
        rv = self._login_employer()
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b"Login successful", rv.data)

    def test_login_wrong_password(self):
        rv = self.client.post("/api/login", json={
            "username": "testcandidate",
            "password": "wrongpassword",
        })
        self.assertEqual(rv.status_code, 401)

    def test_login_unknown_user(self):
        rv = self.client.post("/api/login", json={
            "username": "nobody",
            "password": "anything",
        })
        self.assertEqual(rv.status_code, 401)

    def test_login_missing_fields(self):
        rv = self.client.post("/api/login", json={"username": "testcandidate"})
        self.assertEqual(rv.status_code, 400)

    def test_signup_candidate(self):
        rv = self.client.post("/api/signup", json={
            "account_type": "candidate",
            "username": "newuser",
            "password": "newpass",
            "display_name": "New User",
        })
        self.assertEqual(rv.status_code, 201)

    def test_signup_employer(self):
        rv = self.client.post("/api/signup", json={
            "account_type": "employer",
            "username": "newcorp",
            "password": "corppass",
            "display_name": "New Corp",
        })
        self.assertEqual(rv.status_code, 201)

    def test_signup_duplicate_username(self):
        rv = self.client.post("/api/signup", json={
            "account_type": "candidate",
            "username": "testcandidate",  # already exists
            "password": "pass123",
            "display_name": "Duplicate",
        })
        self.assertEqual(rv.status_code, 409)

    def test_signup_invalid_account_type(self):
        rv = self.client.post("/api/signup", json={
            "account_type": "admin",
            "username": "hacker",
            "password": "hacked",
            "display_name": "Bad Actor",
        })
        self.assertEqual(rv.status_code, 400)

    def test_signup_missing_fields(self):
        rv = self.client.post("/api/signup", json={
            "account_type": "candidate",
            "username": "incomplete",
        })
        self.assertEqual(rv.status_code, 400)



# 2. Candidate Profile Tests


class TestCandidateProfile(BaseTestCase):

    def setUp(self):
        super().setUp()
        self._login_candidate()

    def test_update_profile(self):
        rv = self.client.post("/api/update_profile", json={
            "education": "Master's",
            "major": "Data Science",
            "years_exp": 5,
            "preferred_mode": "Hybrid",
            "preferred_loc": "Melbourne",
        })
        self.assertEqual(rv.status_code, 200)
        # Verify DB was updated
        with app.app_context():
            c = Candidate.query.filter_by(username="testcandidate").first()
            self.assertEqual(c.education, "Master's")
            self.assertEqual(c.years_exp, 5)

    def test_update_profile_unauthenticated(self):
        self.client.get("/logout")
        rv = self.client.post("/api/update_profile", json={"education": "PhD"})
        self.assertEqual(rv.status_code, 401)

    def test_update_skills(self):
        rv = self.client.post("/api/update_skills", json={
            "skills": ["Python", "React", "Docker"]
        })
        self.assertEqual(rv.status_code, 200)
        data = rv.get_json()
        self.assertIn("React", data["skills"])
        self.assertIn("Docker", data["skills"])

    def test_update_skills_creates_new_skill(self):
        rv = self.client.post("/api/update_skills", json={
            "skills": ["Rust"]
        })
        self.assertEqual(rv.status_code, 200)
        with app.app_context():
            skill = Skill.query.filter_by(skill_name="Rust").first()
            self.assertIsNotNone(skill)

    def test_add_work_experience(self):
        rv = self.client.post("/api/work_experience", json={
            "job_title": "Intern Developer",
            "company_name": "Startup Ltd",
        })
        self.assertEqual(rv.status_code, 201)
        data = rv.get_json()
        self.assertIn("id", data)

    def test_add_work_experience_missing_fields(self):
        rv = self.client.post("/api/work_experience", json={
            "job_title": "Developer"
            # missing company_name
        })
        self.assertEqual(rv.status_code, 400)

    def test_delete_work_experience(self):
        # Add one first
        add_rv = self.client.post("/api/work_experience", json={
            "job_title": "Tester",
            "company_name": "QA Corp",
        })
        exp_id = add_rv.get_json()["id"]

        rv = self.client.delete(f"/api/work_experience/{exp_id}")
        self.assertEqual(rv.status_code, 200)

    def test_delete_work_experience_not_found(self):
        rv = self.client.delete("/api/work_experience/99999")
        self.assertEqual(rv.status_code, 404)

    def test_employer_cannot_update_candidate_profile(self):
        # Log in as employer instead
        self.client.get("/logout")
        self._login_employer()
        rv = self.client.post("/api/update_profile", json={"education": "PhD"})
        self.assertEqual(rv.status_code, 401)



# 3. Employer Job Tests


class TestEmployerJobs(BaseTestCase):

    def setUp(self):
        super().setUp()
        self._login_employer()

    def test_create_job(self):
        rv = self.client.post("/api/jobs/create", json={
            "job_title": "Frontend Developer",
            "job_description": "Build UIs.",
            "work_mode": "Remote",
            "job_location": "Brisbane",
            "required_exp": 1,
            "salary_range": "$70,000",
            "required_skills": ["React", "CSS"],
        })
        self.assertEqual(rv.status_code, 201)
        data = rv.get_json()
        self.assertIn("id", data)

    def test_create_job_missing_title(self):
        rv = self.client.post("/api/jobs/create", json={
            "job_description": "No title provided.",
        })
        self.assertEqual(rv.status_code, 400)

    def test_candidate_cannot_create_job(self):
        self.client.get("/logout")
        self._login_candidate()
        rv = self.client.post("/api/jobs/create", json={"job_title": "Test"})
        self.assertEqual(rv.status_code, 401)

    def test_delete_job(self):
        # Create a job, then delete it
        create_rv = self.client.post("/api/jobs/create", json={"job_title": "Temp Job"})
        job_id = create_rv.get_json()["id"]
        rv = self.client.delete(f"/api/jobs/{job_id}")
        self.assertEqual(rv.status_code, 200)

    def test_delete_job_not_owned(self):
        # The seeded job belongs to testemployer; another employer should fail
        self.client.get("/logout")
        self.client.post("/api/signup", json={
            "account_type": "employer",
            "username": "otheremployer",
            "password": "other123",
            "display_name": "Other Corp",
        })
        self.client.post("/api/login", json={
            "username": "otheremployer",
            "password": "other123",
        })
        with app.app_context():
            job = JobPosting.query.first()
            job_id = job.job_id
        rv = self.client.delete(f"/api/jobs/{job_id}")
        self.assertEqual(rv.status_code, 404)



# 4. Browse & Search Tests


class TestSearch(BaseTestCase):

    def test_get_all_candidates(self):
        rv = self.client.get("/api/candidates")
        self.assertEqual(rv.status_code, 200)
        data = rv.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_search_candidates_by_keyword(self):
        rv = self.client.get("/api/candidates?keyword=Test+Candidate")
        data = rv.get_json()
        self.assertTrue(any(c["name"] == "Test Candidate" for c in data))

    def test_search_candidates_by_skill(self):
        rv = self.client.get("/api/candidates?skill=Python")
        data = rv.get_json()
        self.assertTrue(all("Python" in c["skills"] for c in data))

    def test_search_candidates_no_match(self):
        rv = self.client.get("/api/candidates?skill=COBOL")
        data = rv.get_json()
        self.assertEqual(data, [])

    def test_search_candidates_min_exp(self):
        rv = self.client.get("/api/candidates?min_exp=10")
        data = rv.get_json()
        self.assertEqual(data, [])  # seeded candidate has 2 years

    def test_get_all_jobs(self):
        rv = self.client.get("/api/jobs")
        self.assertEqual(rv.status_code, 200)
        data = rv.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_search_jobs_by_keyword(self):
        rv = self.client.get("/api/jobs?keyword=Backend+Developer")
        data = rv.get_json()
        self.assertTrue(any(j["title"] == "Backend Developer" for j in data))

    def test_search_jobs_by_work_mode(self):
        rv = self.client.get("/api/jobs?work_mode=Remote")
        data = rv.get_json()
        self.assertTrue(all(j["work_mode"] == "Remote" for j in data))

    def test_search_jobs_no_match(self):
        rv = self.client.get("/api/jobs?work_mode=OnMars")
        data = rv.get_json()
        self.assertEqual(data, [])



# 5. Applications & Inbox Tests


class TestApplications(BaseTestCase):

    def _get_job_id(self):
        with app.app_context():
            return JobPosting.query.first().job_id

    def test_candidate_can_apply(self):
        self._login_candidate()
        rv = self.client.post("/api/apply", json={"job_id": self._get_job_id()})
        self.assertEqual(rv.status_code, 201)

    def test_cannot_apply_twice(self):
        self._login_candidate()
        job_id = self._get_job_id()
        self.client.post("/api/apply", json={"job_id": job_id})
        rv = self.client.post("/api/apply", json={"job_id": job_id})
        self.assertEqual(rv.status_code, 409)

    def test_apply_missing_job_id(self):
        self._login_candidate()
        rv = self.client.post("/api/apply", json={})
        self.assertEqual(rv.status_code, 400)

    def test_apply_nonexistent_job(self):
        self._login_candidate()
        rv = self.client.post("/api/apply", json={"job_id": 99999})
        self.assertEqual(rv.status_code, 404)

    def test_employer_cannot_apply(self):
        self._login_employer()
        rv = self.client.post("/api/apply", json={"job_id": self._get_job_id()})
        self.assertEqual(rv.status_code, 401)

    def test_employer_can_send_offer(self):
        self._login_employer()
        with app.app_context():
            candidate_id = Candidate.query.first().candidate_id
            job_id = JobPosting.query.first().job_id
        rv = self.client.post("/api/offer", json={
            "candidate_id": candidate_id,
            "job_id": job_id,
        })
        self.assertEqual(rv.status_code, 201)

    def test_candidate_inbox(self):
        # Apply first, then check inbox
        self._login_candidate()
        self.client.post("/api/apply", json={"job_id": self._get_job_id()})
        rv = self.client.get("/api/inbox")
        self.assertEqual(rv.status_code, 200)
        data = rv.get_json()
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]["type"], "application")

    def test_employer_inbox(self):
        # Candidate applies, then employer checks inbox
        self._login_candidate()
        self.client.post("/api/apply", json={"job_id": self._get_job_id()})
        self.client.get("/logout")
        self._login_employer()
        rv = self.client.get("/api/inbox")
        self.assertEqual(rv.status_code, 200)
        data = rv.get_json()
        self.assertGreater(len(data), 0)

    def test_accept_application(self):
        self._login_candidate()
        self.client.post("/api/apply", json={"job_id": self._get_job_id()})
        self.client.get("/logout")
        self._login_employer()
        inbox = self.client.get("/api/inbox").get_json()
        app_id = inbox[0]["id"]
        rv = self.client.post(f"/api/inbox/{app_id}/accept")
        self.assertEqual(rv.status_code, 200)

    def test_reject_application(self):
        self._login_candidate()
        self.client.post("/api/apply", json={"job_id": self._get_job_id()})
        self.client.get("/logout")
        self._login_employer()
        inbox = self.client.get("/api/inbox").get_json()
        app_id = inbox[0]["id"]
        rv = self.client.post(f"/api/inbox/{app_id}/reject")
        self.assertEqual(rv.status_code, 200)

    def test_cannot_accept_others_application(self):
        # Candidate applies, another employer tries to accept
        self._login_candidate()
        self.client.post("/api/apply", json={"job_id": self._get_job_id()})
        self.client.get("/logout")
        self._login_employer()
        inbox = self.client.get("/api/inbox").get_json()
        app_id = inbox[0]["id"]
        # Log in as a different employer
        self.client.get("/logout")
        self.client.post("/api/signup", json={
            "account_type": "employer",
            "username": "otherempl",
            "password": "pass",
            "display_name": "Other",
        })
        self.client.post("/api/login", json={"username": "otherempl", "password": "pass"})
        rv = self.client.post(f"/api/inbox/{app_id}/accept")
        self.assertEqual(rv.status_code, 403)

    def test_inbox_unauthenticated(self):
        rv = self.client.get("/api/inbox")
        self.assertEqual(rv.status_code, 401)



# 6. Recommendations Tests


class TestRecommendations(BaseTestCase):

    def test_job_recommendations_for_candidate(self):
        self._login_candidate()
        rv = self.client.get("/api/recommendations/jobs")
        self.assertEqual(rv.status_code, 200)
        data = rv.get_json()
        self.assertIsInstance(data, list)
        # Seeded job requires Python which candidate has — should appear
        self.assertTrue(any(j["title"] == "Backend Developer" for j in data))

    def test_job_recommendations_unauthenticated(self):
        rv = self.client.get("/api/recommendations/jobs")
        self.assertEqual(rv.status_code, 401)

    def test_job_recommendations_employer_rejected(self):
        self._login_employer()
        rv = self.client.get("/api/recommendations/jobs")
        self.assertEqual(rv.status_code, 401)

    def test_candidate_recommendations_for_employer(self):
        self._login_employer()
        rv = self.client.get("/api/recommendations/candidates")
        self.assertEqual(rv.status_code, 200)
        data = rv.get_json()
        self.assertIsInstance(data, list)
        # Seeded candidate has Python which job requires — should appear
        self.assertTrue(any(c["name"] == "Test Candidate" for c in data))

    def test_candidate_recommendations_unauthenticated(self):
        rv = self.client.get("/api/recommendations/candidates")
        self.assertEqual(rv.status_code, 401)

    def test_candidate_recommendations_with_job_id(self):
        self._login_employer()
        with app.app_context():
            job_id = JobPosting.query.first().job_id
        rv = self.client.get(f"/api/recommendations/candidates?job_id={job_id}")
        self.assertEqual(rv.status_code, 200)



# 7. Membership Tests


class TestMembership(BaseTestCase):

    def test_upgrade_candidate_membership(self):
        self._login_candidate()
        rv = self.client.post("/api/upgrade_membership")
        self.assertEqual(rv.status_code, 200)
        with app.app_context():
            c = Candidate.query.filter_by(username="testcandidate").first()
            self.assertEqual(c.membership_type, "Premium")

    def test_upgrade_employer_membership(self):
        self._login_employer()
        rv = self.client.post("/api/upgrade_membership")
        self.assertEqual(rv.status_code, 200)
        with app.app_context():
            e = Employer.query.filter_by(username="testemployer").first()
            self.assertEqual(e.membership_type, "Premium")

    def test_upgrade_membership_unauthenticated(self):
        rv = self.client.post("/api/upgrade_membership")
        self.assertEqual(rv.status_code, 401)

    def test_premium_gets_unlimited_recommendations(self):
        """Premium candidate should receive all results, not capped at 10."""
        self._login_candidate()
        # Upgrade to premium
        self.client.post("/api/upgrade_membership")
        # Add 15 jobs so free limit of 10 would matter
        self.client.get("/logout")
        self._login_employer()
        for i in range(14):
            self.client.post("/api/jobs/create", json={"job_title": f"Job {i}"})
        self.client.get("/logout")
        self._login_candidate()
        rv = self.client.get("/api/recommendations/jobs")
        data = rv.get_json()
        self.assertGreater(len(data), 10)


if __name__ == "__main__":
    unittest.main()
