"""Google Calendar service — create and list HR-related events."""

from datetime import datetime, timedelta
from typing import Optional
from googleapiclient.discovery import Resource


def create_event(
    calendar: Resource,
    title: str,
    description: str,
    start_datetime: str,
    end_datetime: str,
    attendees: Optional[list[str]] = None,
    location: str = "",
) -> dict:
    """
    Create a calendar event.

    Args:
        start_datetime / end_datetime: ISO 8601 strings, e.g. "2025-06-01T10:00:00"
    """
    event = {
        "summary": title,
        "description": description,
        "location": location,
        "start": {"dateTime": start_datetime, "timeZone": "UTC"},
        "end": {"dateTime": end_datetime, "timeZone": "UTC"},
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 24 * 60},
                {"method": "popup", "minutes": 30},
            ],
        },
    }

    if attendees:
        event["attendees"] = [{"email": addr} for addr in attendees]
        event["sendUpdates"] = "all"

    return calendar.events().insert(calendarId="primary", body=event).execute()


def list_upcoming_events(calendar: Resource, days: int = 7, max_results: int = 20) -> list[dict]:
    """List events for the next N days."""
    now = datetime.utcnow().isoformat() + "Z"
    future = (datetime.utcnow() + timedelta(days=days)).isoformat() + "Z"

    result = calendar.events().list(
        calendarId="primary",
        timeMin=now,
        timeMax=future,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return result.get("items", [])


def format_event_summary(events: list[dict]) -> str:
    """Return a human-readable summary of calendar events."""
    if not events:
        return "No upcoming events."

    lines = []
    for evt in events:
        start = evt["start"].get("dateTime", evt["start"].get("date", ""))
        title = evt.get("summary", "(no title)")
        attendees = [a["email"] for a in evt.get("attendees", [])]
        attendee_str = f" | Attendees: {', '.join(attendees)}" if attendees else ""
        lines.append(f"  • {start[:16].replace('T', ' ')} — {title}{attendee_str}")

    return "\n".join(lines)
