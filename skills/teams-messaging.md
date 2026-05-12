# Skill: Microsoft Teams Messaging

## Metadata
- **Trigger Phrases:** "send to teams", "teams message", "notify team", "message channel"
- **Input Files:** 4 files total (~300 lines)
- **Output Location:** output/teams/[YYYY-MM-DD]/
- **Dependencies:** Microsoft Teams API connected (currently ⬜ PENDING)
- **Execution Time:** ~3 minutes per message
- **Approval Required:** Yes (always preview before sending)

## Input Files (Exact)
1. `skills/teams-messaging.md` (this file)
2. `memory/MEMORY.md` (teams-related sections if any)
3. `docs/teams-api-reference.md` (Teams API patterns)
4. `hr_assistant/teams_service.py` (teams service module)

**Files NOT Loaded:**
- ❌ Email files
- ❌ Payroll files
- ❌ Contract files
- ❌ Calendar files

## Execution Flow
```
User: "Send a message to the team"
  ↓
Check: Teams API connected? (docs/setup-status.md)
↳ Current status: ⬜ PENDING (Anthropic key needed)
Check: Teams credentials valid?
Check: Output folder ready? (output/teams/)
  ↓
Load: 4 input files above
  ↓
Execute:
  1. Get Teams token
  2. Build message
  3. Show preview
  4. Get approval
  5. Send via Microsoft Graph
  6. Log result
  ↓
Output: output/teams/[date]/message_[timestamp].log
  ↓
Verify: Message sent
Confirm: Show confirmation to user
```

## Purpose
Send HR notifications and updates to Teams channels or individual chats
via the Microsoft Graph API.

## Prerequisites
- TEAMS_CLIENT_ID, TEAMS_CLIENT_SECRET, TEAMS_TENANT_ID in .env
- teams_token.json generated after first OAuth login (see docs/teams-api-reference.md)

## Instructions — Send Channel Message
1. Get Teams token from hr_assistant/teams_service.py → get_teams_token()
2. Identify target: team_id + channel_id (from .env or user prompt)
3. Build message body (plain text or simple HTML)
4. POST to: https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages
5. Confirm with user before sending.

## Instructions — Send Direct Chat Message
1. Get Teams token.
2. Identify or create a 1:1 chat: POST /me/chats with the recipient's email.
3. POST message to: /chats/{chat_id}/messages
4. Confirm with user before sending.

## Instructions — Create Teams Meeting
1. Use Microsoft Graph Calendar endpoint: POST /me/events
2. Set isOnlineMeeting: true, onlineMeetingProvider: "teamsForBusiness"
3. The response includes onlineMeeting.joinUrl — add this to the Google Calendar event too.

## Common Mistakes
- Sending without confirmation: always show message preview and ask [S]end / [D]iscard.
- Using expired token: call refresh_teams_token() if a 401 error is returned.
- Wrong endpoint for channel vs. chat: channels use /teams/{id}/channels/{id}/messages,
  chats use /chats/{id}/messages.

## Output Confirmation
```
✓ Teams message sent
  To:      [channel name or recipient email]
  Message: [first 100 chars]...
```
