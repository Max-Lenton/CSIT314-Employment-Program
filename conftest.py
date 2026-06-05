"""
pytest conftest — sets DATABASE_URL before main.py is imported so
Flask-SQLAlchemy uses a temp file instead of the production database.
"""
import os
import tempfile
import warnings

# Suppress SQLAlchemy legacy API deprecation warnings (LegacyAPIWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*legacy.*", category=Warning)
warnings.filterwarnings("ignore", message=".*LegacyAPIWarning.*")

# Must be set BEFORE test_api.py (or any module) imports main.py
_db_fd, _db_path = tempfile.mkstemp(suffix="_test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"


def pytest_sessionfinish(session, exitstatus):
    """Clean up the temp database file after the entire test run."""
    try:
        os.close(_db_fd)
    except OSError:
        pass
    try:
        os.unlink(_db_path)
    except OSError:
        pass
