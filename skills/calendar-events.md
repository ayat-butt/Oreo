# Skill: Calendar Events

## Metadata
- **Trigger Phrases:** "schedule meeting", "create event", "add to calendar", "book time"
- **Input Files:** 4 files total (~250 lines)
- **Output Location:** output/calendar/[YYYY-MM-DD]/
- **Dependencies:** Google Calendar API connected
- **Execution Time:** ~5 minutes per event
- **Approval Required:** Yes (always preview before creating)

## Input Files (Exact)
1. `skills/calendar-events.md` (this file)
2. `memory/MEMORY.md` (calendar-related sections)
3. `hr_assistant/calendar_service.py` (calendar service module)
4. `docs/setup-status.md` (Calendar API status check)

**Files NOT Loaded:**
- ❌ Email files
- ❌ Payroll files
- ❌ Contract files
- ❌ Teams files

## Execution Flow
```
User: "Schedule a meeting with the team"
  ↓
Check: Calendar API connected? (docs/setup-status.md)
Check: Credentials valid?
Check: Output folder ready? (output/calendar/)
  ↓
Load: 4 input files above
  ↓
Execute:
  1. Extract event details (from email or manual input)
  2. Validate date/time
  3. Show preview
  4. Get approval
  5. Create event via Calendar API
  6. Log result
  ↓
Output: output/calendar/[date]/event_[timestamp].md
  ↓
Verify: Event created and invites sent
Confirm: Show calendar link to user
```

## Purpose
Create Google Calendar events and Teams meeting links from email content or manual input.

## Instructions — Extract from Email
1. Pass email subject + body to Claude with prompt:
   "Does this email request a meeting or scheduled event?
    If yes, return JSON: {found, title, description, date (YYYY-MM-DD), time (HH:MM 24h),
    duration_minutes, attendees: [], location}.
    If no, return {found: false}."
2. If date or time is missing, ask the user to provide them.
3. Show a preview of the event before creating it.
4. Create using Google Calendar API: events.insert on primary calendar.
5. If Teams meeting is needed, set conferenceData or add Teams link to description.

## Instructions — Manual Creation
Ask user for: title, date, time, duration, attendees (email list), location/link.
Then follow steps 3-5 above.

## Event Defaults
- Reminder: email 24 hours before + popup 30 minutes before
- Timezone: read from .env or default to UTC
- sendUpdates: "all" (sends invite emails to attendees)

## Output Confirmation
```
✓ Event created
  Title:     [title]
  When:      YYYY-MM-DD HH:MM  (duration min)
  Attendees: email1, email2
  Link:      [Google Calendar URL]
```

## Common Mistakes
- Creating without user confirmation: always show preview first.
- Missing timezone: always set timeZone in start/end objects.
- Not adding Teams link when remote meeting is implied.
