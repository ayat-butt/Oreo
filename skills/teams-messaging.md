# Skill: Microsoft Teams Messaging

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
