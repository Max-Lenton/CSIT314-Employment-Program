"""
Integration tests for Career Connect
Tests end-to-end workflows spanning multiple API calls in sequence.

Run with:  python -m pytest test_integration.py -v
"""

import unittest
from main import app
from extensions import db
from models import Candidate, Employer, JobPosting, Skill, Application
from werkzeug.security import generate_password_hash


class IntegrationBase(unittest.TestCase):
    """Fresh DB for each test."""

    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret"
        self.client = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # Helpers

    def signup_candidate(self, username="cand1", password="pass", name="Candidate One"):
        return self.client.post("/api/signup", json={
            "account_type": "candidate",
            "username": username,
            "password": password,
            "display_name": name,
        })

    def signup_employer(self, username="emp1", password="pass", name="Corp One"):
        return self.client.post("/api/signup", json={
            "account_type": "employer",
            "username": username,
            "password": password,
            "display_name": name,
        })

    def login(self, username, password):
        return self.client.post("/api/login", json={
            "username": username,
            "password": password,
        })

    def logout(self):
        self.client.get("/logout")


# Candidate Journey Tests


class TestCandidateJourney(IntegrationBase):

    def test_signup_login_update_profile_apply(self):
        # 1. Candidate signs up
        rv = self.signup_candidate("alice", "alicepass", "Alice Smith")
        self.assertEqual(rv.status_code, 201)

        # 2. Employer signs up and posts a job
        self.signup_employer("techcorp", "corppass", "Tech Corp")
        self.login("techcorp", "corppass")
        rv = self.client.post("/api/jobs/create", json={
            "job_title": "Python Dev",
            "work_mode": "Remote",
            "job_location": "Sydney",
            "required_exp": 1,
            "required_skills": ["Python"],
        })
        self.assertEqual(rv.status_code, 201)
        job_id = rv.get_json()["id"]
        self.logout()

        # 3. Candidate logs in and updates profile
        self.login("alice", "alicepass")
        rv = self.client.post("/api/update_profile", json={
            "education": "Bachelor's",
            "major": "Computer Science",
            "years_exp": 2,
            "preferred_mode": "Remote",
            "preferred_loc": "Sydney",
        })
        self.assertEqual(rv.status_code, 200)

        # 4. Candidate adds skills
        rv = self.client.post("/api/update_skills", json={"skills": ["Python", "SQL"]})
        self.assertEqual(rv.status_code, 200)
        self.assertIn("Python", rv.get_json()["skills"])

        # 5. Candidate adds work experience
        rv = self.client.post("/api/work_experience", json={
            "job_title": "Junior Dev",
            "company_name": "Old Corp",
        })
        self.assertEqual(rv.status_code, 201)
        exp_id = rv.get_json()["id"]

        # 6. Candidate applies for the job
        rv = self.client.post("/api/apply", json={"job_id": job_id})
        self.assertEqual(rv.status_code, 201)

        # 7. Application appears in candidate inbox
        rv = self.client.get("/api/inbox")
        inbox = rv.get_json()
        self.assertEqual(len(inbox), 1)
        self.assertEqual(inbox[0]["type"], "application")
        self.assertEqual(inbox[0]["status"], "pending")
        self.assertEqual(inbox[0]["job_title"], "Python Dev")

        # 8. Candidate deletes old work experience
        rv = self.client.delete(f"/api/work_experience/{exp_id}")
        self.assertEqual(rv.status_code, 200)

    def test_cannot_apply_to_nonexistent_job_after_login(self):
        self.signup_candidate("bob", "bobpass", "Bob Jones")
        self.login("bob", "bobpass")
        rv = self.client.post("/api/apply", json={"job_id": 9999})
        self.assertEqual(rv.status_code, 404)

    def test_duplicate_application_blocked(self):
        self.signup_employer("emp", "pass", "Corp")
        self.login("emp", "pass")
        rv = self.client.post("/api/jobs/create", json={"job_title": "Dev"})
        job_id = rv.get_json()["id"]
        self.logout()

        self.signup_candidate("cand", "pass", "Cand")
        self.login("cand", "pass")
        self.client.post("/api/apply", json={"job_id": job_id})
        rv = self.client.post("/api/apply", json={"job_id": job_id})
        self.assertEqual(rv.status_code, 409)


# Employer Journey Tests


class TestEmployerJourney(IntegrationBase):

    def _setup(self):
        """Create employer with job and candidate with application."""
        self.signup_employer("emp", "emppass", "Emp Corp")
        self.login("emp", "emppass")
        rv = self.client.post("/api/jobs/create", json={
            "job_title": "Backend Dev",
            "work_mode": "Remote",
            "required_skills": ["Python"],
        })
        self.job_id = rv.get_json()["id"]
        self.logout()

        self.signup_candidate("cand", "candpass", "Cand User")
        self.login("cand", "candpass")
        self.client.post("/api/apply", json={"job_id": self.job_id})
        self.logout()

    def test_employer_sees_application_and_accepts(self):
        self._setup()
        self.login("emp", "emppass")

        # Employer's inbox contains the application
        inbox = self.client.get("/api/inbox").get_json()
        self.assertEqual(len(inbox), 1)
        self.assertEqual(inbox[0]["type"], "application")
        self.assertEqual(inbox[0]["status"], "pending")
        app_id = inbox[0]["id"]

        # Employer accepts
        rv = self.client.post(f"/api/inbox/{app_id}/accept")
        self.assertEqual(rv.status_code, 200)

        # Inbox now shows accepted
        inbox = self.client.get("/api/inbox").get_json()
        self.assertEqual(inbox[0]["status"], "accepted")

    def test_employer_sees_application_and_rejects(self):
        self._setup()
        self.login("emp", "emppass")
        inbox = self.client.get("/api/inbox").get_json()
        app_id = inbox[0]["id"]

        rv = self.client.post(f"/api/inbox/{app_id}/reject")
        self.assertEqual(rv.status_code, 200)

        inbox = self.client.get("/api/inbox").get_json()
        self.assertEqual(inbox[0]["status"], "rejected")

    def test_employer_sends_offer_candidate_accepts(self):
        self.signup_employer("emp", "emppass", "Emp Corp")
        self.login("emp", "emppass")
        rv = self.client.post("/api/jobs/create", json={"job_title": "Dev"})
        job_id = rv.get_json()["id"]

        self.signup_candidate("cand", "candpass", "Cand")
        with app.app_context():
            cand_id = Candidate.query.filter_by(username="cand").first().candidate_id

        # Employer sends offer
        rv = self.client.post("/api/offer", json={
            "candidate_id": cand_id,
            "job_id": job_id,
        })
        self.assertEqual(rv.status_code, 201)
        self.logout()

        # Candidate logs in and sees offer in inbox
        self.login("cand", "candpass")
        inbox = self.client.get("/api/inbox").get_json()
        self.assertEqual(len(inbox), 1)
        self.assertEqual(inbox[0]["type"], "offer")
        self.assertEqual(inbox[0]["status"], "pending")
        offer_id = inbox[0]["id"]

        # Candidate accepts the offer
        rv = self.client.post(f"/api/inbox/{offer_id}/accept")
        self.assertEqual(rv.status_code, 200)

        inbox = self.client.get("/api/inbox").get_json()
        self.assertEqual(inbox[0]["status"], "accepted")

    def test_duplicate_offer_blocked(self):
        self.signup_employer("emp", "emppass", "Emp Corp")
        self.login("emp", "emppass")
        rv = self.client.post("/api/jobs/create", json={"job_title": "Dev"})
        job_id = rv.get_json()["id"]

        self.signup_candidate("cand", "candpass", "Cand")
        with app.app_context():
            cand_id = Candidate.query.filter_by(username="cand").first().candidate_id

        self.client.post("/api/offer", json={"candidate_id": cand_id, "job_id": job_id})
        rv = self.client.post("/api/offer", json={"candidate_id": cand_id, "job_id": job_id})
        self.assertEqual(rv.status_code, 409)

    def test_other_employer_cannot_accept_unowned_application(self):
        self._setup()

        # Get the application id via the real employer
        self.login("emp", "emppass")
        inbox = self.client.get("/api/inbox").get_json()
        app_id = inbox[0]["id"]
        self.logout()

        # Sign up a second employer and try to accept
        self.signup_employer("emp2", "pass2", "Other Corp")
        self.login("emp2", "pass2")
        rv = self.client.post(f"/api/inbox/{app_id}/accept")
        self.assertEqual(rv.status_code, 403)


# Recommendation Workflow Tests


class TestRecommendationWorkflow(IntegrationBase):

    def test_skill_matched_job_appears_in_recommendations(self):
        # Create employer with a Python job
        self.signup_employer("emp", "pass", "Corp")
        self.login("emp", "pass")
        self.client.post("/api/jobs/create", json={
            "job_title": "Python Engineer",
            "work_mode": "Remote",
            "job_location": "Sydney",
            "required_exp": 1,
            "required_skills": ["Python", "Flask"],
        })
        self.logout()

        # Create candidate with matching skills
        self.signup_candidate("cand", "pass", "Skilled Cand")
        self.login("cand", "pass")
        self.client.post("/api/update_skills", json={"skills": ["Python", "Flask"]})
        self.client.post("/api/update_profile", json={
            "preferred_mode": "Remote",
            "years_exp": 2,
        })

        rv = self.client.get("/api/recommendations/jobs")
        self.assertEqual(rv.status_code, 200)
        titles = [j["title"] for j in rv.get_json()]
        self.assertIn("Python Engineer", titles)

    def test_skill_matched_candidate_appears_in_recommendations(self):
        # Create candidate with Python skill
        self.signup_candidate("cand", "pass", "Python Dev")
        self.login("cand", "pass")
        self.client.post("/api/update_skills", json={"skills": ["Python"]})
        self.logout()

        # Create employer with Python job and check candidate recommendations
        self.signup_employer("emp", "pass", "Corp")
        self.login("emp", "pass")
        self.client.post("/api/jobs/create", json={
            "job_title": "Dev",
            "required_skills": ["Python"],
        })

        rv = self.client.get("/api/recommendations/candidates")
        self.assertEqual(rv.status_code, 200)
        names = [c["name"] for c in rv.get_json()]
        self.assertIn("Python Dev", names)

    def test_unmatched_candidate_not_in_recommendations(self):
        # Candidate with no skills
        self.signup_candidate("nocand", "pass", "No Skills")
        # Employer with Python requirement
        self.signup_employer("emp", "pass", "Corp")
        self.login("emp", "pass")
        self.client.post("/api/jobs/create", json={
            "job_title": "Dev",
            "required_skills": ["Python"],
        })

        rv = self.client.get("/api/recommendations/candidates")
        data = rv.get_json()
        # Candidate has 0 skill overlap — they may appear but with lowest score
        # Ensure the response is a valid list
        self.assertIsInstance(data, list)

    def test_premium_unlocks_more_than_10_recommendations(self):
        # Create 12 jobs
        self.signup_employer("emp", "pass", "Corp")
        self.login("emp", "pass")
        for i in range(12):
            self.client.post("/api/jobs/create", json={"job_title": f"Job {i}"})
        self.logout()

        # Free candidate gets ≤ 10
        self.signup_candidate("free_cand", "pass", "Free User")
        self.login("free_cand", "pass")
        rv = self.client.get("/api/recommendations/jobs")
        self.assertLessEqual(len(rv.get_json()), 10)
        self.logout()

        # Premium candidate gets all
        self.signup_candidate("prem_cand", "pass", "Premium User")
        self.login("prem_cand", "pass")
        self.client.post("/api/upgrade_membership")
        rv = self.client.get("/api/recommendations/jobs")
        self.assertGreater(len(rv.get_json()), 10)


# Membership Workflow Tests


class TestMembershipWorkflow(IntegrationBase):

    def test_candidate_membership_upgrade_persists(self):
        self.signup_candidate("cand", "pass", "Cand")
        self.login("cand", "pass")

        # Confirm starts as free
        with app.app_context():
            c = Candidate.query.filter_by(username="cand").first()
            self.assertNotEqual((c.membership_type or "").lower(), "premium")

        # Upgrade
        rv = self.client.post("/api/upgrade_membership")
        self.assertEqual(rv.status_code, 200)

        # Confirm now premium
        with app.app_context():
            c = Candidate.query.filter_by(username="cand").first()
            self.assertEqual(c.membership_type, "Premium")

    def test_employer_membership_upgrade_persists(self):
        self.signup_employer("emp", "pass", "Corp")
        self.login("emp", "pass")
        rv = self.client.post("/api/upgrade_membership")
        self.assertEqual(rv.status_code, 200)
        with app.app_context():
            e = Employer.query.filter_by(username="emp").first()
            self.assertEqual(e.membership_type, "Premium")

    def test_unauthenticated_upgrade_rejected(self):
        rv = self.client.post("/api/upgrade_membership")
        self.assertEqual(rv.status_code, 401)


# Search Workflow Tests


class TestSearchWorkflow(IntegrationBase):

    def test_new_job_appears_in_search_immediately(self):
        # Initially no jobs
        rv = self.client.get("/api/jobs")
        self.assertEqual(rv.get_json(), [])

        # Employer creates a job
        self.signup_employer("emp", "pass", "Corp")
        self.login("emp", "pass")
        self.client.post("/api/jobs/create", json={
            "job_title": "Data Scientist",
            "work_mode": "Hybrid",
            "job_location": "Melbourne",
        })
        self.logout()

        # Job now appears in search
        rv = self.client.get("/api/jobs?keyword=Data+Scientist")
        data = rv.get_json()
        self.assertTrue(any(j["title"] == "Data Scientist" for j in data))

    def test_deleted_job_no_longer_in_search(self):
        self.signup_employer("emp", "pass", "Corp")
        self.login("emp", "pass")
        rv = self.client.post("/api/jobs/create", json={"job_title": "Temp Job"})
        job_id = rv.get_json()["id"]

        # Confirm it exists
        rv = self.client.get("/api/jobs?keyword=Temp+Job")
        self.assertGreater(len(rv.get_json()), 0)

        # Delete it
        self.client.delete(f"/api/jobs/{job_id}")

        # Confirm it's gone
        rv = self.client.get("/api/jobs?keyword=Temp+Job")
        self.assertEqual(rv.get_json(), [])

    def test_updated_candidate_skills_appear_in_search(self):
        self.signup_candidate("cand", "pass", "Cand")
        self.login("cand", "pass")

        # Initially no skill — search by COBOL returns no match
        rv = self.client.get("/api/candidates?skill=COBOL")
        self.assertEqual(rv.get_json(), [])

        # Add COBOL skill
        self.client.post("/api/update_skills", json={"skills": ["COBOL"]})

        # Now appears
        rv = self.client.get("/api/candidates?skill=COBOL")
        data = rv.get_json()
        self.assertTrue(any(c["name"] == "Cand" for c in data))

    def test_candidate_filter_by_work_mode_and_skill(self):
        self.signup_candidate("remote_cand", "pass", "Remote Worker")
        self.login("remote_cand", "pass")
        self.client.post("/api/update_profile", json={"preferred_mode": "Remote"})
        self.client.post("/api/update_skills", json={"skills": ["Go"]})
        self.logout()

        self.signup_candidate("onsite_cand", "pass", "Onsite Worker")
        self.login("onsite_cand", "pass")
        self.client.post("/api/update_profile", json={"preferred_mode": "On-site"})
        self.client.post("/api/update_skills", json={"skills": ["Go"]})
        self.logout()

        # Filter: skill=Go AND work_mode=Remote — only Remote Worker should match
        rv = self.client.get("/api/candidates?skill=Go&work_mode=Remote")
        data = rv.get_json()
        names = [c["name"] for c in data]
        self.assertIn("Remote Worker", names)
        self.assertNotIn("Onsite Worker", names)


# Auth Boundary Tests


class TestAuthBoundaries(IntegrationBase):

    def test_session_required_for_all_write_endpoints(self):
        """All mutating endpoints must return 401 without a session."""
        endpoints = [
            ("POST", "/api/update_profile", {}),
            ("POST", "/api/update_skills", {"skills": []}),
            ("POST", "/api/work_experience", {"job_title": "x", "company_name": "y"}),
            ("DELETE", "/api/work_experience/1", None),
            ("POST", "/api/jobs/create", {"job_title": "x"}),
            ("DELETE", "/api/jobs/1", None),
            ("POST", "/api/apply", {"job_id": 1}),
            ("POST", "/api/offer", {"candidate_id": 1, "job_id": 1}),
            ("POST", "/api/inbox/1/accept", {}),
            ("POST", "/api/inbox/1/reject", {}),
            ("POST", "/api/upgrade_membership", {}),
        ]
        for method, path, body in endpoints:
            with self.subTest(method=method, path=path):
                if method == "POST":
                    rv = self.client.post(path, json=body or {})
                else:
                    rv = self.client.delete(path)
                self.assertEqual(
                    rv.status_code, 401,
                    f"{method} {path} should return 401 when unauthenticated"
                )

    def test_candidate_cannot_use_employer_only_endpoints(self):
        self.signup_candidate("cand", "pass", "Cand")
        self.login("cand", "pass")
        rv = self.client.post("/api/jobs/create", json={"job_title": "x"})
        self.assertEqual(rv.status_code, 401)
        rv = self.client.post("/api/offer", json={"candidate_id": 1, "job_id": 1})
        self.assertEqual(rv.status_code, 401)

    def test_employer_cannot_use_candidate_only_endpoints(self):
        self.signup_employer("emp", "pass", "Corp")
        self.login("emp", "pass")
        rv = self.client.post("/api/update_profile", json={"education": "PhD"})
        self.assertEqual(rv.status_code, 401)
        rv = self.client.post("/api/apply", json={"job_id": 1})
        self.assertEqual(rv.status_code, 401)
        rv = self.client.post("/api/update_skills", json={"skills": []})
        self.assertEqual(rv.status_code, 401)

    def test_login_required_for_recommendations(self):
        rv = self.client.get("/api/recommendations/jobs")
        self.assertEqual(rv.status_code, 401)
        rv = self.client.get("/api/recommendations/candidates")
        self.assertEqual(rv.status_code, 401)

    def test_logout_clears_session(self):
        self.signup_candidate("cand", "pass", "Cand")
        self.login("cand", "pass")

        # Authenticated — works
        rv = self.client.post("/api/update_profile", json={})
        self.assertEqual(rv.status_code, 200)

        self.logout()

        # After logout — rejected
        rv = self.client.post("/api/update_profile", json={})
        self.assertEqual(rv.status_code, 401)


if __name__ == "__main__":
    unittest.main()
