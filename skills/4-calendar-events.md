# Skill 4: Calendar Events

## Metadata
- **Trigger Phrases:** "schedule meeting", "add calendar", "book time", "create event", "invite to meeting", "calendar invite"
- **Input Files:** 4 files total (~250 lines)
- **Output Location:** output/calendar/[YYYY-MM-DD]/
- **Dependencies:** Google Calendar API connected, Anthropic API available
- **Execution Time:** ~3 minutes per event
- **Approval Required:** YES — Always preview before creating

## Input Files (Exact)
1. `skills/4-calendar-events.md` (this file)
2. `memory/MEMORY.md` (calendar-related sections)
3. `docs/google-calendar-api-reference.md` (Calendar API patterns)
4. `memory/feedback_calendar_*.md` (calendar rules if any)

**Files NOT Loaded:**
- ❌ Email categorisation files
- ❌ Payroll files
- ❌ Contract files
- ❌ Teams files
- ❌ Probation files

## Execution Flow
```
User: "Schedule a meeting with John and Jane for tomorrow at 2pm"
  ↓
Check: Google Calendar API connected? (docs/setup-status.md)
Check: User has calendar access?
Check: Output folder ready? (output/calendar/)
  ↓
Load: 4 input files above
  ↓
Execute:
  1. Parse meeting details (attendees, date, time, title, description)
  2. Verify attendee email addresses (look up if needed)
  3. Check availability/conflicts (optional)
  4. Build event details
  5. Show preview to user
  6. Get approval: [C]reate / [E]dit / [C]ancel
  7. Create event via Google Calendar API
  8. Log output
  ↓
Output: output/calendar/[date]/event_[timestamp].md
  ↓
Verify: Event created and accessible
Confirm: Show details and attendee list to user
```

## Purpose
Schedule HR meetings, interviews, reviews, and team events in Google Calendar with automatic attendee invitations and confirmation logging.

## Mandatory Rules (LOCKED)

### Rule 1: Always Confirm Attendee Emails
- Never guess email addresses
- Ask user for confirmation: "Is this the right email?" [john@company.com]
- If unsure: look up in company directory or ask user
- Wrong email = wrong person invited

### Rule 2: Check for Conflicts
Before creating:
- Check user's calendar for conflicts
- Check attendees' availability if possible
- Alert user: "Attendee X has a conflict at that time"
- Offer alternative times if conflicts found

### Rule 3: Include Full Event Details
Every event must have:
- **Title:** Clear, descriptive (e.g., "1:1 Review with John", not "Meeting")
- **Date & Time:** Specific, timezone-aware
- **Duration:** Typical: 30 min (1:1), 60 min (group)
- **Location/Meet Link:** Virtual or in-person address
- **Description:** Purpose, agenda, any prep needed
- **Attendees:** Full list with emails

### Rule 4: Offer Google Meet Link Option
- Ask: "Add Google Meet link?" [Y/N]
- If YES: Create Teams meeting URL too (if Teams meeting)
- If NO: Assume in-person or call details to follow

### Rule 5: Send Invitations
- Create event with attendee emails
- Google Calendar automatically sends invitations
- No additional email needed
- Attendees see in calendar and can RSVP

### Rule 6: Always Preview Before Creating
- Show user: title, date, time, attendees, duration, description
- Format clearly and readably
- Get explicit approval: [C]reate / [E]dit / [C]ancel
- Never auto-create without approval

### Rule 7: Log Event Details
- Save event summary to output/calendar/
- Include: timestamp, attendees, outcome
- Track all events created in a session
- Log is record of what was scheduled

### Rule 8: Timezone Awareness
- Always clarify timezone for international attendees
- Default: Use user's timezone (from .env or system)
- Example: "2pm EST" or "2pm PKT"
- Store timezone in event (Google Calendar handles this)

## Event Templates (LOCKED)

### Template 1: 1:1 Meeting
```
Title: 1:1 Review with [Employee Name]
Date: [YYYY-MM-DD]
Time: [HH:MM AM/PM] [Timezone]
Duration: 30 minutes
Attendees: [Manager Email], [Employee Email]
Description:
  Monthly 1:1 review session
  Agenda:
  - Performance feedback
  - Goals and objectives
  - Career development
  - Any concerns or feedback
```

### Template 2: Interview
```
Title: Interview — [Candidate Name] for [Position]
Date: [YYYY-MM-DD]
Time: [HH:MM AM/PM] [Timezone]
Duration: 45-60 minutes
Attendees: [Interviewer 1 Email], [Interviewer 2 Email], [Candidate Email]
Description:
  Interview for [Position] role
  Candidate: [Name]
  Interview Format: [Technical / Behavioral / HR]
  Panel: [Names]
  Google Meet: [Link if virtual]
```

### Template 3: Team Meeting
```
Title: Team Meeting — [Team Name] [Month]
Date: [YYYY-MM-DD]
Time: [HH:MM AM/PM] [Timezone]
Duration: 60 minutes
Attendees: [List all 8+ attendees]
Location: [Conference Room or Google Meet Link]
Description:
  Monthly team sync-up
  Agenda:
  - Updates and announcements
  - Project reviews
  - Open discussion
  - Q&A
```

### Template 4: Training/Onboarding
```
Title: [Type] Training — [Employee Name]
Date: [YYYY-MM-DD]
Time: [HH:MM AM/PM] [Timezone]
Duration: 120 minutes
Attendees: [Trainer Email], [Trainee Email]
Location: [Office or Google Meet]
Description:
  [Training Type]: Onboarding session
  Topics to cover:
  - Company overview
  - Systems access
  - Team introductions
  - First day logistics
```

## Common Mistakes (LOCKED)

❌ **Mistake 1: Wrong Email Address**
- Verify every email before creating event
- Ask user: "Is this the right email?"
- Wrong email = wrong person invited, event is useless

❌ **Mistake 2: Missing Attendees**
- List ALL attendees explicitly
- Don't assume who should be invited
- Ask user: "Anyone else who should attend?"
- Missing attendee = incomplete meeting

❌ **Mistake 3: Vague Event Title**
- "Meeting" is too generic
- Use: "1:1 Review with John", "Interview — Jane for Developer"
- Title should tell attendees what the event is

❌ **Mistake 4: No Event Description/Agenda**
- Always include purpose or agenda
- Attendees need context for what to expect
- Include any prep work needed
- Description is more than just a title

❌ **Mistake 5: No Duration Specified**
- Always specify meeting length
- Examples: 30 min (1:1), 60 min (meeting), 45 min (interview)
- Duration helps attendees block time

❌ **Mistake 6: Forgetting Timezone**
- Always include timezone if not obvious
- International teams need clarity
- "2pm EST" not just "2pm"
- Google Calendar stores timezone

❌ **Mistake 7: Not Checking Conflicts**
- Check user's calendar for conflicts
- Ask attendees about availability if possible
- Offer alternative times if conflicts found
- Don't schedule over existing events

❌ **Mistake 8: Creating Without Preview**
- Always show user preview first
- Display: title, date, time, attendees, duration
- Get explicit approval: [C]reate / [E]dit / [C]ancel
- Never auto-create

## Output Format (LOCKED)

**File:** output/calendar/[YYYY-MM-DD]/event_[timestamp].md

```
# Calendar Event Created
**Date:** 2026-05-12  
**Time:** 15:45:03 UTC  
**Status:** Event Created Successfully

---

## Event Details
- **Title:** 1:1 Review with John Smith
- **Date:** 2026-05-14 (Tuesday)
- **Time:** 2:00 PM — 2:30 PM (EST)
- **Duration:** 30 minutes
- **Location:** Google Meet: [link]
- **Organizer:** ayat@taleemabad.com

---

## Attendees (2 total)
1. ✓ Ayat Khan (ayat@taleemabad.com) — Organizer
2. ✓ John Smith (john.smith@taleemabad.com) — Invited

**Invitations sent:** 1 (to John Smith)

---

## Event Description
Monthly 1:1 review session

Agenda:
- Performance feedback
- Goals and objectives
- Career development
- Any concerns or feedback

---

## Confirmation
✓ Event created in Google Calendar
  Title: 1:1 Review with John Smith
  Attendees: 2 (John invited)
  Invitations: Sent to 1 attendee
  Google Meet: [Link created]
  
  Action: John will receive calendar invite
```

## Instructions — Step by Step

1. **Gather Meeting Details**
   ```
   Meeting Title: [required] → "What is the meeting title?"
   Attendees: [required] → "Who should be invited? (email addresses)"
   Date: [required] → "What date? (YYYY-MM-DD)"
   Time: [required] → "What time? (HH:MM AM/PM and timezone)"
   Duration: [recommended] → "How long? (default 30-60 min)"
   Location: [optional] → "Where? (in-person or Google Meet)"
   Description: [optional] → "What is the agenda?"
   ```

2. **Verify Attendee Emails**
   ```
   Attendees:
   - john.smith@taleemabad.com [Is this correct? Y/N]
   - jane.doe@taleemabad.com [Is this correct? Y/N]
   - [Confirm each email]
   ```

3. **Check for Conflicts**
   ```
   Checking calendar for conflicts...
   - Your calendar: No conflict
   - John Smith: Available
   - Jane Doe: Conflict (already has "Team Meeting" 2:30-3:30pm)
   
   Suggested time: 2:00 PM — 2:30 PM (before conflict)
   Accept? [Y/N]
   ```

4. **Build Event Details**
   - Create event object with all details
   - Format title, description, attendee list
   - Include timezone and duration

5. **Display Preview**
   ```
   Event Preview:
   
   Title: 1:1 Review with John Smith
   Date: Tuesday, 2026-05-14
   Time: 2:00 PM — 2:30 PM (EST)
   Attendees: John Smith (john.smith@taleemabad.com)
   Google Meet: [Link to be created]
   
   Agenda: Monthly 1:1 review session
   ```

6. **Get Approval**
   ```
   Create this event?
   [C]reate / [E]dit details / [C]ancel
   ```

7. **Create Event via API**
   ```python
   service.events().insert(
       calendarId='primary',
       body={
           'summary': title,
           'description': description,
           'start': {'dateTime': start_time, 'timeZone': timezone},
           'end': {'dateTime': end_time, 'timeZone': timezone},
           'attendees': [{'email': email} for email in attendees],
           'conferenceData': {
               'createRequest': {
                   'requestId': str(uuid.uuid4()),
                   'conferenceSolution': {
                       'key': {'type': 'hangoutsMeet'}
                   }
               }
           }
       },
       conferenceDataVersion=1
   ).execute()
   ```

8. **Log Event Details**
   - Save to output/calendar/[date]/event_[timestamp].md
   - Include all event details and confirmation

9. **Confirm to User**
   ```
   ✓ Event created successfully
   Title: 1:1 Review with John Smith
   Date: Tuesday, May 14, 2026 at 2:00 PM EST
   Attendees: John Smith (invited)
   Google Meet: [Link]
   
   Calendar: Saved to user's Google Calendar
   Invite: John will receive calendar invite
   ```

---

**Skill Status:** ✅ ACTIVE  
**Integration:** ✅ Google Calendar API  
**Approval Required:** YES (always preview)  
**Conflicts Check:** Recommended (optional)  
**Google Meet:** Optional (user choice)  
**Data Safety:** All events visible in Google Calendar
