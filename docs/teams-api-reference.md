# Microsoft Teams API Reference (Microsoft Graph)

## Authentication
- Type: OAuth 2.0 via MSAL (Microsoft Authentication Library)
- Requires: Azure App Registration (free, takes ~10 minutes)
- Token stored in: teams_token.json

## Azure App Registration — What You Need
Go to portal.azure.com → Azure Active Directory → App Registrations → New Registration.
Record these three values (store in .env):
- Application (client) ID  → TEAMS_CLIENT_ID
- Directory (tenant) ID    → TEAMS_TENANT_ID
- Client Secret            → TEAMS_CLIENT_SECRET (create under Certificates & Secrets)

## Permissions Required (Delegated)
Add these in Azure → your app → API Permissions → Add Permission → Microsoft Graph:
- Chat.ReadWrite          (send/read direct messages)
- ChannelMessage.Send     (send channel messages)
- Calendars.ReadWrite     (create Teams meetings)
- User.Read               (read own profile)

## Key Graph Endpoints
| Action                     | Endpoint |
|----------------------------|---------|
| Send channel message       | POST /teams/{team_id}/channels/{channel_id}/messages |
| List my chats              | GET /me/chats |
| Send direct message        | POST /chats/{chat_id}/messages |
| Create Teams meeting       | POST /me/events (with isOnlineMeeting: true) |
| Get team list              | GET /me/joinedTeams |
| Get team channels          | GET /teams/{team_id}/channels |

## Base URL
https://graph.microsoft.com/v1.0/

## Auth Flow (Delegated — requires user login)
```python
import msal
app = msal.PublicClientApplication(CLIENT_ID, authority=f"https://login.microsoftonline.com/{TENANT_ID}")
result = app.acquire_token_interactive(scopes=["https://graph.microsoft.com/.default"])
token = result["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
```

## Message Body Format
```json
{
  "body": {
    "contentType": "text",
    "content": "Your message here"
  }
}
```
