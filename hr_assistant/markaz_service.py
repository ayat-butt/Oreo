"""Markaz HRMS integration — REST API client for markaz.taleemabad.com"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("MARKAZ_BASE_URL", "https://markaz.taleemabad.com")
_session = requests.Session()
_session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
_token = None


# ── Auth ─────────────────────────────────────────────────────────────────────

def login(email: str = None, password: str = None) -> str:
    """Login to Markaz and return JWT token. Caches token for the session."""
    global _token
    email = email or os.getenv("MARKAZ_EMAIL")
    password = password or os.getenv("MARKAZ_PASSWORD")
    if not email or not password:
        raise ValueError("MARKAZ_EMAIL and MARKAZ_PASSWORD must be set in .env")
    r = _session.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password})
    r.raise_for_status()
    data = r.json()
    _token = data.get("token") or data.get("access_token") or data.get("accessToken")
    if not _token:
        # Some APIs set token via cookie — check cookies
        _token = r.cookies.get("token") or r.cookies.get("auth_token") or r.cookies.get("session")
    if _token:
        _session.headers.update({"Authorization": f"Bearer {_token}"})
    return _token


def get_current_user():
    """Return the logged-in user's profile."""
    _ensure_auth()
    return _get("/api/auth/user")


def logout():
    """Logout and clear token."""
    global _token
    _session.post(f"{BASE_URL}/api/auth/logout")
    _token = None
    _session.headers.pop("Authorization", None)


# ── Employees ────────────────────────────────────────────────────────────────

def get_employees(params: dict = None):
    """List all employees. Optional filter params e.g. {'department': 'P&C'}"""
    _ensure_auth()
    return _get("/api/employees", params=params)


def get_employee(employee_id):
    """Get a single employee by ID."""
    _ensure_auth()
    return _get(f"/api/employees/{employee_id}")


def get_employee_profile(user_id):
    """Get detailed profile for a user."""
    _ensure_auth()
    return _get(f"/api/employee-profiles/{user_id}")


def get_users(params: dict = None):
    """List all users (system accounts)."""
    _ensure_auth()
    return _get("/api/users", params=params)


def get_users_with_profiles(params: dict = None):
    """List users with their employee profiles joined."""
    _ensure_auth()
    return _get("/api/users-with-profiles", params=params)


def create_user(payload: dict):
    """Create a new user account in Markaz."""
    _ensure_auth()
    return _post("/api/users/create", payload)


def invite_user(payload: dict):
    """Send an invite to a new employee."""
    _ensure_auth()
    return _post("/api/users/invite", payload)


# ── Leave & Overtime ─────────────────────────────────────────────────────────

def get_my_leave_requests():
    """Get leave requests for the logged-in user."""
    _ensure_auth()
    return _get("/api/leave-requests")


def get_all_leave_requests(params: dict = None):
    """Get all leave requests (admin view). Filter by status, date, etc."""
    _ensure_auth()
    return _get("/api/all-leave-requests", params=params)


def get_team_leave_requests():
    """Get leave requests for the user's team (manager view)."""
    _ensure_auth()
    return _get("/api/team-leave-requests")


def get_my_overtime_requests():
    """Get overtime requests for the logged-in user."""
    _ensure_auth()
    return _get("/api/overtime-requests")


def get_all_overtime_requests(params: dict = None):
    """Get all overtime requests (admin view)."""
    _ensure_auth()
    return _get("/api/all-overtime-requests", params=params)


def get_team_overtime_requests():
    """Get overtime requests for the user's team (manager view)."""
    _ensure_auth()
    return _get("/api/team-overtime-requests")


# ── Payroll & Salary ─────────────────────────────────────────────────────────

def get_payroll(params: dict = None):
    """Get payroll records."""
    _ensure_auth()
    return _get("/api/payroll", params=params)


def get_employee_payroll(params: dict = None):
    """Get employee payroll details."""
    _ensure_auth()
    return _get("/api/employee-payroll", params=params)


def get_salary_history(params: dict = None):
    """Get salary history records."""
    _ensure_auth()
    return _get("/api/salary-history", params=params)


def get_salary_information():
    """Get current salary information."""
    _ensure_auth()
    return _get("/api/salary-information")


def get_advance_requests():
    """Get advance salary requests."""
    _ensure_auth()
    return _get("/api/advance-requests")


def get_all_advance_requests():
    """Get all advance requests (admin view)."""
    _ensure_auth()
    return _get("/api/all-advance-requests")


def get_loan_requests():
    """Get loan requests."""
    _ensure_auth()
    return _get("/api/loan-requests")


# ── Documents ────────────────────────────────────────────────────────────────

def generate_document(payload: dict):
    """Generate an HR document (payslip, experience letter, etc.)."""
    _ensure_auth()
    return _post("/api/documents/generate", payload)


def get_document_history(params: dict = None):
    """Get history of generated documents."""
    _ensure_auth()
    return _get("/api/documents/history", params=params)


def send_proof_of_employment(payload: dict):
    """Send proof of employment letter."""
    _ensure_auth()
    return _post("/api/documents/send-proof-of-employment", payload)


def send_bank_account_opening_letter(payload: dict):
    """Send bank account opening letter."""
    _ensure_auth()
    return _post("/api/documents/send-bank-account-opening", payload)


# ── Onboarding ───────────────────────────────────────────────────────────────

def get_onboarding(params: dict = None):
    """Get onboarding records."""
    _ensure_auth()
    return _get("/api/onboarding", params=params)


# ── Notifications & Reminders ────────────────────────────────────────────────

def get_notifications():
    """Get notifications for the logged-in user."""
    _ensure_auth()
    return _get("/api/notifications")


def get_notification_count():
    """Get unread notification count."""
    _ensure_auth()
    return _get("/api/notifications/count")


def mark_all_notifications_viewed():
    """Mark all notifications as viewed."""
    _ensure_auth()
    return _post("/api/notifications/mark-all-viewed", {})


def get_reminder_history(params: dict = None):
    """Get history of sent reminders."""
    _ensure_auth()
    return _get("/api/reminder-history", params=params)


# ── Departments & Roles ──────────────────────────────────────────────────────

def get_departments():
    """List all departments."""
    _ensure_auth()
    return _get("/api/departments")


def get_roles():
    """List all roles."""
    _ensure_auth()
    return _get("/api/roles")


def get_job_titles():
    """List all job titles."""
    _ensure_auth()
    return _get("/api/job-titles")


# ── Recruitment ──────────────────────────────────────────────────────────────

def get_jobs(params: dict = None):
    """List job openings."""
    _ensure_auth()
    return _get("/api/jobs", params=params)


def get_candidates(params: dict = None):
    """List candidates."""
    _ensure_auth()
    return _get("/api/candidates", params=params)


def get_applications(params: dict = None):
    """List job applications."""
    _ensure_auth()
    return _get("/api/applications", params=params)


# ── Performance & Assessments ────────────────────────────────────────────────

def get_performance_reviews(params: dict = None):
    """Get performance reviews."""
    _ensure_auth()
    return _get("/api/performance-reviews", params=params)


def get_analytics(params: dict = None):
    """Get HR analytics data."""
    _ensure_auth()
    return _get("/api/analytics", params=params)


def get_engagement_surveys(params: dict = None):
    """Get engagement survey data."""
    _ensure_auth()
    return _get("/api/engagement-surveys", params=params)


# ── Assets ───────────────────────────────────────────────────────────────────

def get_assets(params: dict = None):
    """List company assets."""
    _ensure_auth()
    return _get("/api/assets", params=params)


def get_asset_assignments(params: dict = None):
    """List asset assignments to employees."""
    _ensure_auth()
    return _get("/api/asset-assignments", params=params)


# ── Attendance ───────────────────────────────────────────────────────────────

def get_attendance(params: dict = None):
    """Get attendance records."""
    _ensure_auth()
    return _get("/api/attendance", params=params)


# ── Internal helpers ─────────────────────────────────────────────────────────

def _ensure_auth():
    if not _token and not _session.headers.get("Authorization"):
        login()


def _get(path: str, params: dict = None):
    r = _session.get(f"{BASE_URL}{path}", params=params)
    r.raise_for_status()
    return r.json()


def _post(path: str, payload: dict):
    r = _session.post(f"{BASE_URL}{path}", json=payload)
    r.raise_for_status()
    return r.json()


def _patch(path: str, payload: dict):
    r = _session.patch(f"{BASE_URL}{path}", json=payload)
    r.raise_for_status()
    return r.json()


def _delete(path: str):
    r = _session.delete(f"{BASE_URL}{path}")
    r.raise_for_status()
    return r.json()
