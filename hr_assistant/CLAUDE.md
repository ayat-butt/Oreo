# HR Assistant Services — Development Guide

## What This Directory Is
Core Python service modules for Gmail, Google Calendar, Microsoft Teams, Google Drive, and contract generation. These are the **integration layer** between Claude and external services.

## Module Structure

### Authentication & Configuration
- `config.py` — Environment variables, paths, company defaults
- `audit_log.py` — Logging all sensitive operations

### Google Workspace Services
- `gmail_service.py` — Gmail API client setup
- `calendar_service.py` — Google Calendar operations
- `drive_service.py` — Google Drive file operations
- `markaz_service.py` — Markaz database read-only access

### Business Logic
- `contract_service.py` — Contract generation and management
- `email_service.py` — HR email drafting and sending
- `teams_service.py` — Microsoft Teams messaging
- `claude_assistant.py` — Claude AI integration

### Database
- `markaz_db.py` — Read-only Markaz employee database

## When to Edit This
- Adding a new integration (Teams, Slack, etc.)
- Fixing an authentication bug
- Improving existing service methods

## When NOT to Edit This
- For one-off data operations → use fetch_sheets_data.py instead
- For payroll logic → go to payroll/ folder
- For HR workflows → use skills/ folder instead

## Important Rules

1. **Never hardcode credentials** — Use config.py
2. **Never write to Markaz** — Read-only only (see [feedback_markaz_readonly.md](../memory/feedback_markaz_readonly.md))
3. **Always log sensitive operations** → audit_log.py
4. **Test before deployment** — Test in dev environment first
5. **Follow PEP 8** — Type hints required for all functions

## Common Patterns

### Creating a new service
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def new_service():
    creds = load_credentials()
    return build('service_name', 'v1', credentials=creds)
```

### Error handling
```python
try:
    result = service.execute()
except HttpError as error:
    log_error(f"API error: {error}")
    raise
```

---
**Last updated:** 2026-05-12
