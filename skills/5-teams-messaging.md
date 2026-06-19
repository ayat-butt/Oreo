# Skill 5: Microsoft Teams Messaging

## Metadata
- **Trigger Phrases:** "send to teams", "teams message", "notify team", "message channel", "teams notification"
- **Input Files:** 4 files total (~300 lines)
- **Output Location:** output/teams/[YYYY-MM-DD]/
- **Dependencies:** Microsoft Teams API connected, Anthropic API available
- **Execution Time:** ~3 minutes per message
- **Approval Required:** YES — Always preview before sending
- **Status:** ⬜ PENDING (Teams API needs Anthropic key to enable)

## Input Files (Exact)
1. `skills/5-teams-messaging.md` (this file)
2. `memory/MEMORY.md` (teams-related sections if any)
3. `docs/teams-api-reference.md` (Teams API patterns)
4. `hr_assistant/teams_service.py` (teams service module)

**Files NOT Loaded:**
- ❌ Email categorisation files
- ❌ Payroll files
- ❌ Contract files
- ❌ Calendar files
- ❌ Probation files

## Execution Flow
```
User: "Send a message to the team"
  ↓
Check: Teams API connected? (docs/setup-status.md)
  Current: ⬜ PENDING (Anthropic key needed)
Check: Teams credentials valid?
Check: Output folder ready? (output/teams/)
  ↓
Load: 4 input files above
  ↓
Execute:
  1. Get Teams token (use refresh_teams_token if needed)
  2. Identify target: team_id + channel_id (or direct chat recipient)
  3. Build message (plain text or simple HTML)
  4. Show preview to user
  5. Get approval: [S]end / [D]iscard
  6. Send via Microsoft Graph API
  7. Log result
  ↓
Output: output/teams/[date]/message_[timestamp].log
  ↓
Verify: Message sent successfully
Confirm: Show confirmation to user
```

## Purpose
Send HR notifications and updates to Teams channels or individual chats via the Microsoft Graph API. Used for announcements, policy updates, event notifications, and team communications.

## Prerequisites (LOCKED)

**Before Teams skill can be activated:**
1. ✅ TEAMS_CLIENT_ID in .env
2. ✅ TEAMS_CLIENT_SECRET in .env
3. ✅ TEAMS_TENANT_ID in .env
4. ⬜ ANTHROPIC_API_KEY in .env (REQUIRED to unlock Teams)
5. ✅ teams_token.json generated after first OAuth login

**Current Status:** PENDING Teams API connection (waiting for Anthropic key)

## Message Types (LOCKED)

### Type 1: Channel Message
**Use:** Broadcast to team channel

**Details:**
```
- Target: Channel in a team
- Endpoint: /teams/{team_id}/channels/{channel_id}/messages
- Visibility: All team members see it
- Example: HR policy update to #announcements
```

### Type 2: Direct Chat Message
**Use:** Private message to individual

**Details:**
```
- Target: 1:1 chat with person
- Endpoint: /chats/{chat_id}/messages
- Visibility: Only recipient sees it
- Example: Performance review notification to John
```

### Type 3: Group Chat Message
**Use:** Message to group of people

**Details:**
```
- Target: Group chat (multiple recipients)
- Endpoint: /chats/{chat_id}/messages
- Visibility: Only group members see it
- Example: Team announcement to HR group
```

## Mandatory Rules (LOCKED)

### Rule 1: Always Preview Before Sending
- Show user: recipient (channel/person/group), message content
- Display full message text
- Get explicit approval: [S]end / [D]iscard
- Never auto-send

### Rule 2: Use Simple Formatting
- Plain text preferred
- Simple HTML allowed: bold, italics, line breaks
- No complex HTML or attachments (Teams has limits)
- Test formatting with user before sending

### Rule 3: Verify Token Before Sending
- Check teams_token.json exists
- If 401 error during send: call refresh_teams_token()
- Get fresh token and retry
- If fails again: inform user, don't auto-retry

### Rule 4: Identify Target Correctly
- Channel message: need team_id + channel_id
- Direct chat: need recipient email or user ID
- Ask user: "Send to channel or direct message?"
- Confirm target: "Channel #announcements?" or "Direct message to John?"

### Rule 5: Log Every Send
- Save to output/teams/[date]/message_[timestamp].log
- Include: timestamp, recipient, message content, status (sent/failed)
- Track all messages sent in session
- Log is record for audit trail

### Rule 6: Handle Errors Gracefully
- If send fails: show error to user
- Don't auto-retry silently
- Ask user: "Try again?" or "Cancel?"
- Log error reason

### Rule 7: Respect User Availability
- Note: Direct messages notify user immediately
- Large announcements may need timing consideration
- Ask: "Send immediately or schedule?" (if scheduling available)
- Don't send during off-hours without warning

### Rule 8: Keep Messages Concise
- Channel announcements: under 300 words
- Direct messages: under 200 words
- Complex info: break into multiple messages
- Include next steps or action items

## Message Templates (LOCKED)

### Template 1: Policy Announcement
```
Title: [Policy Name] Update — Action Required

Channel: #announcements
Recipients: All staff

Message:
Dear Team,

We have updated our [Policy Name] effective [DATE].

Key changes:
- [Change 1]
- [Change 2]
- [Change 3]

Please review the updated policy at: [Link]

If you have questions, reach out to HR.

Best regards,
HR Team, Taleemabad
```

### Template 2: Event Notification
```
Title: [Event Name] — You're Invited

Channel: #general or Direct to [Person]
Recipients: [Specific people or all]

Message:
Hi [Name/Team],

We're excited to announce [Event Name]

When: [Date and time]
Where: [Location or Teams link]
RSVP: [Link or instructions]

We look forward to seeing you!

Best regards,
[Event organizer]
```

### Template 3: HR Notification (Individual)
```
Title: [Notification Type] — [Employee Name]

Type: Direct chat
Recipient: [Employee email]

Message:
Hi [Name],

[Notification content]

Next steps: [What they should do]

Please confirm receipt of this message.

Best regards,
HR Team, Taleemabad
```

### Template 4: System Update
```
Title: [System Name] Maintenance — Scheduled Downtime

Channel: #it or #announcements
Recipients: [All or specific team]

Message:
Team,

[System] will be down for maintenance:

Start: [Date and time]
Duration: [X hours]
Impact: [What is affected]
Alternative: [What to use instead]

Contact [Support] for issues.

Thank you for your patience.
```

## Common Mistakes (LOCKED)

❌ **Mistake 1: Sending Without Preview**
- Always show message before sending
- Typos and formatting errors visible in preview
- Get user confirmation: [S]end / [D]iscard
- Never auto-send

❌ **Mistake 2: Using Expired Token**
- Check teams_token.json before sending
- If 401 error: refresh token and retry
- Don't ignore "token invalid" errors
- Always verify token is current

❌ **Mistake 3: Wrong Recipient (Channel vs Direct)**
- Channel message = everyone sees it
- Direct message = only recipient sees it
- Confirm before sending: "Channel #general?" or "Direct to John?"
- Wrong recipient = message to wrong place

❌ **Mistake 4: Complex Formatting**
- Don't use complex HTML
- Teams has formatting limits
- Test simple formatting with user first
- Keep it plain text + simple HTML

❌ **Mistake 5: No Token Handling**
- teams_token.json must exist
- If missing: generate with OAuth first
- If expired: refresh before sending
- Never send without valid token

❌ **Mistake 6: Forgetting to Log**
- Always save message log to output/teams/
- Include: timestamp, recipient, content, status
- Logging is not optional
- Audit trail required

❌ **Mistake 7: Exceeding Message Limits**
- Channel announcements: under 300 words
- Direct messages: under 200 words
- If longer: split into multiple messages
- Teams has character limits

❌ **Mistake 8: Not Handling Errors**
- If send fails: inform user immediately
- Show error message
- Ask: "Try again?" or "Cancel?"
- Don't auto-retry silently

## Output Format (LOCKED)

**File:** output/teams/[YYYY-MM-DD]/message_[timestamp].log

```
# Teams Message Log
**Date:** 2026-05-12  
**Time:** 16:30:02 UTC  
**Status:** Sent Successfully

---

## Message Details
- **Type:** Channel Message
- **Recipient:** #announcements (Team: Engineering)
- **Sender:** HR System
- **Approval:** YES

---

## Message Content

Subject: HR Policy Update — Remote Work Policy

Dear Team,

We have updated our Remote Work Policy effective 2026-06-01.

Key changes:
- Hybrid work: 3 days office, 2 days remote per week
- No more fully remote (unless approved by manager)
- Meeting schedule: Focus on office days for in-person collaboration

Please review the updated policy at: [Link to policy document]

If you have questions, reach out to HR.

Best regards,
HR Team, Taleemabad

---

## Metadata
- **Message ID:** 1234567890
- **Sent To:** 87 team members (Engineering channel)
- **Delivery:** Confirmed
- **Reactions:** [user can add reactions in Teams]

---

## Confirmation
✓ Message sent successfully
  Type: Channel announcement
  Channel: #announcements
  Recipients: 87 team members
  Content: [First 100 chars]...
  Time: 2026-05-12 at 4:30 PM
  
  Status: Delivered and visible to all channel members
```

## Instructions — Step by Step

1. **Check Integration Status**
   ```
   Read: docs/setup-status.md
   Status: Teams API = ⬜ PENDING
   
   NOTE: Teams API not yet active
   REASON: Waiting for Anthropic API key
   ACTION: Add ANTHROPIC_API_KEY to .env to unlock
   ```

2. **Get Teams Token**
   ```python
   from hr_assistant.teams_service import get_teams_token
   
   token = get_teams_token()  # Retrieves from teams_token.json
   if not token:
       raise Exception("Teams token not found — run OAuth setup first")
   ```

3. **Build Message**
   ```
   Message type: [Channel / Direct / Group]
   Recipient: [#channel_name or @email or Group name]
   Content: [Message text]
   Format: [Plain text or simple HTML]
   ```

4. **Identify Target**
   - Channel: Get team_id + channel_id from Teams admin
   - Direct: Get recipient email or user ID
   - Group: Get chat_id from Teams

5. **Display Preview**
   ```
   Message Preview:
   
   To: #announcements
   
   "Dear Team, We have updated our Remote Work Policy..."
   [Show full message]
   ```

6. **Get Approval**
   ```
   Send this message?
   [S]end / [D]iscard
   ```

7. **Send via Microsoft Graph**
   ```python
   import requests
   
   # For channel message:
   url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages"
   
   payload = {
       'body': {
           'contentType': 'html',
           'content': message_html
       }
   }
   
   headers = {'Authorization': f'Bearer {token}'}
   response = requests.post(url, json=payload, headers=headers)
   
   # For direct message:
   url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"
   response = requests.post(url, json=payload, headers=headers)
   ```

8. **Log Results**
   - Save to output/teams/[date]/message_[timestamp].log
   - Include all details: recipient, content, status

9. **Confirm to User**
   ```
   ✓ Message sent successfully
   Recipient: #announcements
   Type: Channel announcement
   Visibility: 87 team members
   Time: 2026-05-12 at 4:30 PM
   
   Output: output/teams/2026-05-12/message_163002.log
   ```

## Error Handling (LOCKED)

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Token expired | Call refresh_teams_token() |
| 403 Forbidden | No permission for channel | Verify user is channel member |
| 404 Not Found | Channel/user not found | Verify team_id/channel_id/email |
| 429 Too Many Requests | Rate limited | Wait and retry in 60 seconds |
| 500 Server Error | Teams API issue | Wait and retry or contact Teams support |

---

**Skill Status:** ⬜ PENDING ACTIVATION  
**Integration:** ⬜ Teams API (waiting for Anthropic key)  
**Approval Required:** YES (always preview)  
**Direct Send:** ❌ NO (preview required)  
**Token Refresh:** Automatic (if expired)  
**Logging:** Required (audit trail)  

---

**⚠️ TO ACTIVATE THIS SKILL:**
Add `ANTHROPIC_API_KEY=[your-key]` to `.env` file.
Once added, Teams messaging will be available immediately.
