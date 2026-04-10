"""Markaz HRMS — direct PostgreSQL integration via Neon.tech.

READ-ONLY by default. Write operations require explicit call to write-enabled functions.
Credentials stored in .env as MARKAZ_DB_URL — never hardcoded.
"""

import os
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("MARKAZ_DB_URL")


@contextmanager
def _conn():
    """Context manager — opens connection, yields cursor, closes cleanly."""
    conn = psycopg2.connect(DB_URL)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        yield cur, conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Employees ────────────────────────────────────────────────────────────────

def get_all_employees(active_only=True):
    """Return all employees with their profiles joined."""
    with _conn() as (cur, _):
        where = "WHERE u.deleted_at IS NULL AND u.archived_at IS NULL" if active_only else ""
        cur.execute(f"""
            SELECT
                u.id, u.first_name, u.last_name, u.email,
                u.hire_date, u.status, u.job_title, u.work_location,
                u.last_sign_in_at, u.is_admin,
                ep.employee_id, ep.department, ep.payroll_entity,
                ep.joining_date, ep.gender, ep.contact_number,
                ep.gross_salary, ep.bank_name, ep.cnic_number,
                ep.level, ep.line_manager_id, ep.official_email,
                d.name AS department_name
            FROM users u
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            LEFT JOIN departments d ON u.department_id = d.id
            {where}
            ORDER BY u.first_name, u.last_name
        """)
        return cur.fetchall()


def get_employee_by_name(name: str):
    """Search employee by first or last name (case-insensitive)."""
    with _conn() as (cur, _):
        cur.execute("""
            SELECT
                u.id, u.first_name, u.last_name, u.email,
                u.hire_date, u.status, u.job_title,
                ep.employee_id, ep.department, ep.payroll_entity,
                ep.joining_date, ep.gross_salary, ep.cnic_number,
                ep.official_email, ep.contact_number
            FROM users u
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            WHERE u.deleted_at IS NULL
              AND (
                  LOWER(u.first_name || ' ' || u.last_name) LIKE LOWER(%s)
                  OR LOWER(u.first_name) LIKE LOWER(%s)
                  OR LOWER(u.last_name) LIKE LOWER(%s)
              )
            ORDER BY u.first_name
        """, (f"%{name}%", f"%{name}%", f"%{name}%"))
        return cur.fetchall()


def get_employee_by_id(user_id: str):
    """Get full employee record by user ID."""
    with _conn() as (cur, _):
        cur.execute("""
            SELECT u.*, ep.*,
                   d.name AS department_name
            FROM users u
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            LEFT JOIN departments d ON u.department_id = d.id
            WHERE u.id = %s
        """, (user_id,))
        return cur.fetchone()


def get_employees_by_department(department: str):
    """Get all active employees in a department."""
    with _conn() as (cur, _):
        cur.execute("""
            SELECT u.id, u.first_name, u.last_name, u.email,
                   u.hire_date, u.job_title, ep.payroll_entity, ep.joining_date
            FROM users u
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            WHERE u.deleted_at IS NULL
              AND u.archived_at IS NULL
              AND LOWER(ep.department) LIKE LOWER(%s)
            ORDER BY u.first_name
        """, (f"%{department}%",))
        return cur.fetchall()


def get_employees_hired_between(start_date: str, end_date: str):
    """Get employees who joined between two dates (YYYY-MM-DD format)."""
    with _conn() as (cur, _):
        cur.execute("""
            SELECT u.id, u.first_name, u.last_name, u.email,
                   ep.joining_date, ep.department, ep.payroll_entity,
                   u.job_title, ep.employee_id
            FROM users u
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            WHERE u.deleted_at IS NULL
              AND ep.joining_date BETWEEN %s AND %s
            ORDER BY ep.joining_date
        """, (start_date, end_date))
        return cur.fetchall()


def get_headcount_by_department():
    """Return headcount grouped by department."""
    with _conn() as (cur, _):
        cur.execute("""
            SELECT ep.department, COUNT(*) AS headcount
            FROM users u
            JOIN employee_profiles ep ON u.id = ep.user_id
            WHERE u.deleted_at IS NULL AND u.archived_at IS NULL
            GROUP BY ep.department
            ORDER BY headcount DESC
        """)
        return cur.fetchall()


# ── Leave Requests ───────────────────────────────────────────────────────────

def get_pending_leave_requests():
    """Get all pending leave requests with employee names."""
    with _conn() as (cur, _):
        cur.execute("""
            SELECT lr.id, lr.user_id, lr.leave_type, lr.reason, lr.status,
                   lr.start_date::text, lr.end_date::text,
                   lr.approver_comments, lr.created_at, lr.sub_category, lr.is_half_day,
                   u.first_name || ' ' || u.last_name AS employee_name,
                   u.email AS employee_email,
                   ep.department, ep.payroll_entity
            FROM leave_requests lr
            JOIN users u ON lr.user_id = u.id
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            WHERE lr.status = 'pending'
            ORDER BY lr.created_at DESC
        """)
        return cur.fetchall()


def get_leave_requests(status: str = None, user_id: str = None):
    """Get leave requests, optionally filtered by status or user."""
    with _conn() as (cur, _):
        conditions = []
        params = []
        if status:
            conditions.append("lr.status = %s")
            params.append(status)
        if user_id:
            conditions.append("lr.user_id = %s")
            params.append(user_id)
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        cur.execute(f"""
            SELECT lr.*,
                   u.first_name || ' ' || u.last_name AS employee_name,
                   ep.department
            FROM leave_requests lr
            JOIN users u ON lr.user_id = u.id
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            {where}
            ORDER BY lr.created_at DESC
        """, params)
        return cur.fetchall()


# ── Overtime Requests ────────────────────────────────────────────────────────

def get_pending_overtime_requests():
    """Get all pending overtime requests."""
    with _conn() as (cur, _):
        cur.execute("""
            SELECT ot.*,
                   u.first_name || ' ' || u.last_name AS employee_name,
                   u.email AS employee_email,
                   ep.department, ep.payroll_entity
            FROM overtime_requests ot
            JOIN users u ON ot.user_id = u.id
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            WHERE ot.status = 'pending'
            ORDER BY ot.created_at DESC
        """)
        return cur.fetchall()


def get_overtime_requests(status: str = None):
    """Get overtime requests optionally filtered by status."""
    with _conn() as (cur, _):
        where = "WHERE ot.status = %s" if status else ""
        params = [status] if status else []
        cur.execute(f"""
            SELECT ot.*,
                   u.first_name || ' ' || u.last_name AS employee_name,
                   ep.department
            FROM overtime_requests ot
            JOIN users u ON ot.user_id = u.id
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            {where}
            ORDER BY ot.created_at DESC
        """, params)
        return cur.fetchall()


# ── Salary & Payroll ─────────────────────────────────────────────────────────

def get_salary_history(user_id: str = None):
    """Get salary history, optionally for a specific employee."""
    with _conn() as (cur, _):
        where = "WHERE sh.user_id = %s" if user_id else ""
        params = [user_id] if user_id else []
        cur.execute(f"""
            SELECT sh.*,
                   u.first_name || ' ' || u.last_name AS employee_name
            FROM salary_history sh
            JOIN users u ON sh.user_id = u.id
            {where}
            ORDER BY sh.created_at DESC
        """, params)
        return cur.fetchall()


def get_advance_requests(status: str = None):
    """Get advance salary requests."""
    with _conn() as (cur, _):
        where = "WHERE ar.status = %s" if status else ""
        params = [status] if status else []
        cur.execute(f"""
            SELECT ar.*,
                   u.first_name || ' ' || u.last_name AS employee_name,
                   ep.department
            FROM advance_requests ar
            JOIN users u ON ar.user_id = u.id
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            {where}
            ORDER BY ar.created_at DESC
        """, params)
        return cur.fetchall()


def get_loan_requests(status: str = None):
    """Get loan requests."""
    with _conn() as (cur, _):
        where = "WHERE lr.status = %s" if status else ""
        params = [status] if status else []
        cur.execute(f"""
            SELECT lr.*,
                   u.first_name || ' ' || u.last_name AS employee_name
            FROM loan_requests lr
            JOIN users u ON lr.user_id = u.id
            {where}
            ORDER BY lr.created_at DESC
        """, params)
        return cur.fetchall()


# ── Notifications ────────────────────────────────────────────────────────────

def get_notifications(user_id: str = None, unread_only: bool = False):
    """Get notifications, optionally filtered by user or unread status."""
    with _conn() as (cur, _):
        conditions = []
        params = []
        if user_id:
            conditions.append("user_id = %s")
            params.append(user_id)
        if unread_only:
            conditions.append("is_read = FALSE")
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        cur.execute(f"""
            SELECT * FROM notifications
            {where}
            ORDER BY created_at DESC
            LIMIT 100
        """, params)
        return cur.fetchall()


def send_notification(user_id: str, title: str, message: str, notif_type: str = "info", related_id: int = None):
    """Insert a notification for a user. Requires explicit call — always preview first."""
    with _conn() as (cur, conn):
        cur.execute("""
            INSERT INTO notifications (user_id, title, message, type, related_id, is_read, is_viewed, created_at)
            VALUES (%s, %s, %s, %s, %s, FALSE, FALSE, NOW())
            RETURNING id
        """, (user_id, title, message, notif_type, related_id))
        conn.commit()
        return cur.fetchone()


# ── Departments ──────────────────────────────────────────────────────────────

def get_departments():
    """List all active departments."""
    with _conn() as (cur, _):
        cur.execute("SELECT * FROM departments WHERE is_active = TRUE ORDER BY name")
        return cur.fetchall()


# ── Probation (custom — not a native Markaz table) ───────────────────────────

def get_employees_on_probation():
    """Return employees whose 3-month probation has ended or is ending within 14 days.
    Based on joining_date from employee_profiles."""
    with _conn() as (cur, _):
        cur.execute("""
            SELECT
                u.id, u.first_name, u.last_name, u.email,
                ep.joining_date, ep.department, ep.payroll_entity,
                u.job_title,
                ep.joining_date + INTERVAL '3 months' AS probation_end_date,
                EXTRACT(DAY FROM (ep.joining_date + INTERVAL '3 months' - CURRENT_DATE))::int AS days_remaining
            FROM users u
            JOIN employee_profiles ep ON u.id = ep.user_id
            WHERE u.deleted_at IS NULL
              AND u.archived_at IS NULL
              AND ep.joining_date IS NOT NULL
              AND ep.joining_date + INTERVAL '3 months' <= CURRENT_DATE + INTERVAL '14 days'
              AND ep.joining_date >= CURRENT_DATE - INTERVAL '12 months'
            ORDER BY probation_end_date ASC
        """)
        return cur.fetchall()


# ── Recruitment ──────────────────────────────────────────────────────────────

def get_active_jobs():
    """Get all active job postings."""
    with _conn() as (cur, _):
        cur.execute("""
            SELECT * FROM jobs
            WHERE status = 'active' OR status = 'published'
            ORDER BY created_at DESC
        """)
        return cur.fetchall()


def get_candidates(status: str = None):
    """Get candidates, optionally filtered by status."""
    with _conn() as (cur, _):
        where = "WHERE status = %s" if status else ""
        params = [status] if status else []
        cur.execute(f"SELECT * FROM candidates {where} ORDER BY created_at DESC", params)
        return cur.fetchall()


# ── Activity & Audit ─────────────────────────────────────────────────────────

def get_recent_activity(limit: int = 50):
    """Get recent activity log entries."""
    with _conn() as (cur, _):
        cur.execute("""
            SELECT al.*,
                   u.first_name || ' ' || u.last_name AS user_name
            FROM activity_logs al
            LEFT JOIN users u ON al.user_id = u.id
            ORDER BY al.created_at DESC
            LIMIT %s
        """, (limit,))
        return cur.fetchall()


# ── Quick stats ──────────────────────────────────────────────────────────────

def get_dashboard_stats():
    """Return a quick summary of key HR metrics."""
    with _conn() as (cur, _):
        stats = {}
        queries = {
            "total_employees":       "SELECT COUNT(*) FROM users WHERE deleted_at IS NULL AND archived_at IS NULL",
            "pending_leaves":        "SELECT COUNT(*) FROM leave_requests WHERE status = 'pending'",
            "pending_overtime":      "SELECT COUNT(*) FROM overtime_requests WHERE status = 'pending'",
            "pending_advances":      "SELECT COUNT(*) FROM advance_requests WHERE status = 'pending'",
            "unread_notifications":  "SELECT COUNT(*) FROM notifications WHERE is_read = FALSE",
            "open_jobs":             "SELECT COUNT(*) FROM jobs",
            "total_candidates":      "SELECT COUNT(*) FROM candidates",
        }
        for key, query in queries.items():
            cur.execute(query)
            row = cur.fetchone()
            stats[key] = list(row.values())[0] if row else 0
        return stats
