# CSIT314 Employment Program

An employment matching web application built for CSIT314 Systems Development Methodologies.

Candidates can create profiles, list skills and work experience, upload resumes, and browse/receive recommended job postings. Employers can post jobs with required skills, browse candidates, and receive recommended matches. Both account types support Standard and Premium membership tiers.

---

## Requirements

- Python 3.9+
- Flask
- Flask-SQLAlchemy
- pytest (for running tests)

### Install dependencies

```
pip install Flask Flask-SQLAlchemy pytest
```

To verify: `flask --version` / `pip show sqlalchemy`

---

## Setup

### 1. Seed the database

Populates the SQLite database with demo accounts and sample data. **Run this before first use, or to reset the database.**

```
python seed.py
```

### Demo accounts

| Role      | Username        | Password   |
|-----------|-----------------|------------|
| Candidate | `demo`          | `Demo1234!` |
| Employer  | `demo_employer` | `Demo1234!` |

---

## Running the app

```
flask --app main run --debug
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

Press `Ctrl+C` to stop.

---

## Running the tests

All tests run against an isolated temporary database and never touch the production data.

```
# Unit tests only
python -m pytest test_api.py -v

# Integration tests only
python -m pytest test_integration.py -v

# Both together
python -m pytest test_api.py test_integration.py -v
```

### Unit tests — `test_api.py` (55 tests)

Test individual API endpoints in isolation.

| Suite | What is tested |
|---|---|
| `TestAuth` | Login, signup, invalid credentials, duplicate usernames |
| `TestCandidateProfile` | Profile updates, skills, work experience |
| `TestEmployerJobs` | Job creation, deletion, authorization |
| `TestSearch` | Candidate/job search with keyword, skill, location, exp filters |
| `TestApplications` | Apply, offer, inbox, accept/reject, auth enforcement |
| `TestRecommendations` | Job & candidate recommendations, premium limits |
| `TestMembership` | Membership upgrade, premium unlocks unlimited results |

### Integration tests — `test_integration.py` (24 tests)

Test end-to-end workflows spanning multiple API calls in sequence.

| Suite | Workflow tested |
|---|---|
| `TestCandidateJourney` | Signup → profile setup → skills → apply → inbox → delete experience |
| `TestEmployerJourney` | Post job → accept/reject application → send offer → candidate accepts |
| `TestRecommendationWorkflow` | Skill-matched results appear; premium unlocks >10 results |
| `TestMembershipWorkflow` | Upgrade persists to DB; unauthenticated upgrade rejected |
| `TestSearchWorkflow` | New jobs appear immediately; deleted jobs disappear; filters update live |
| `TestAuthBoundaries` | All 11 write endpoints return 401 when unauthenticated; role separation enforced; logout clears session |

Key test files:

```
test_api.py           # Unit tests (55 tests)
test_integration.py   # Integration tests (24 tests)
conftest.py           # Redirects DB to a temp file before tests run
pytest.ini            # Suppresses deprecation warnings from output
```

---

## Project structure

```
main.py              # Flask app — all routes and API endpoints
models.py            # SQLAlchemy ORM models
extensions.py        # SQLAlchemy instance
seed.py              # DB seed script
test_api.py              # Unit tests (55 tests)
test_integration.py      # Integration tests (24 tests)
conftest.py              # pytest config — isolates test DB
pytest.ini               # pytest warning filters
static/
  css/style.css      # Global styles (dark theme)
  js/                # Page logic (jobs.js, employees.js, candidate_profile.js, employer_profile.js, login.js, signup.js)
  uploads/resumes/   # Uploaded candidate resumes (PDF)
templates/
  login.html
  homepage.html
  jobs.html
  employees.html
  candidate_profile.html
  employer_profile.html
instance/
  database.db        # SQLite database (auto-created)
```

---

## Features

- **Auth** — signup/login for candidate and employer account types
- **Candidate profile** — education, major, years of experience, work mode preference, location, skills, work history, resume upload
- **Employer profile** — company job postings with required skills, salary, location, work mode
- **Job search** — fuzzy keyword search with filters for work mode, location, and experience
- **Candidate search** — fuzzy keyword search with filters for skill, education, experience, and work mode
- **Recommendations** — skill-overlap scoring to match candidates to jobs and vice versa
- **Membership** — Standard (top 10 recommendations) vs Premium (unlimited)
