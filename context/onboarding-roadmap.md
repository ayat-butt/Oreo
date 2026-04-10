# Onboarding Roadmap — Baby Steps

Complete one baby step at a time. Tick it off in docs/setup-status.md when done.
Each step should take 15–30 minutes. Do NOT move to the next step until the current one works.

---

## BABY STEP 1 — Anthropic (Claude) API Key
Goal: Make sure Claude can think.

1. Go to https://console.anthropic.com → API Keys → Create Key
2. Copy the key
3. Open .env in the project folder (copy from .env.example first)
4. Set: ANTHROPIC_API_KEY=your_key_here
5. Test: run `python -c "import anthropic; print('Claude ready')"` in terminal
6. Mark ✅ in docs/setup-status.md

---

## BABY STEP 2 — Google Cloud Project + Enable APIs
Goal: Get permission from Google to use Gmail and Calendar.

1. Go to https://console.cloud.google.com
2. Create a new project (e.g. "HR Assistant")
3. Go to APIs & Services → Library
4. Enable these four APIs one by one:
   - Gmail API
   - Google Calendar API
   - Google Drive API
   - Google Docs API
5. Note: no credentials yet — just enabling access

---

## BABY STEP 3 — Google OAuth Credentials
Goal: Create the "key" that lets the agent log in to your Google account.

1. In Google Cloud Console → APIs & Services → Credentials
2. Click Create Credentials → OAuth 2.0 Client ID
3. Application type: Desktop app
4. Name: HR Assistant
5. Download the JSON file
6. Rename it credentials.json
7. Move it into the project root: c:/Agent Oreo/credentials.json
8. Mark 🔄 In Progress in docs/setup-status.md

---

## BABY STEP 4 — Test Gmail Connection
Goal: Confirm the agent can read your Gmail.

1. Open terminal in c:/Agent Oreo
2. Run: pip install -r requirements.txt
3. Run: python main.py
4. First run will open a browser — log in with your Google account and click Allow
5. A file called token.json will be created (this is your saved login)
6. In the menu, choose option 7 (Email Briefing Summary)
7. If you see email subjects listed → Gmail is working ✅
8. Mark ✅ Gmail in docs/setup-status.md

---

## BABY STEP 5 — Test Google Calendar Connection
Goal: View your upcoming calendar events from the agent.

1. In main.py menu, choose option 4 (View Upcoming Events)
2. If you see a list of your events → Calendar is working ✅
3. Mark ✅ Google Calendar in docs/setup-status.md

---

## BABY STEP 6 — Azure App Registration (Teams)
Goal: Get credentials to connect to Microsoft Teams.

1. Go to https://portal.azure.com
2. Search for "Azure Active Directory" → App registrations → New registration
3. Name: HR Assistant Teams Bot
4. Account type: Accounts in this organizational directory only
5. Redirect URI: http://localhost  (type: Public client / native)
6. Click Register — copy the Application (client) ID and Directory (tenant) ID
7. Go to Certificates & Secrets → New client secret → copy the Value
8. Go to API Permissions → Add Permission → Microsoft Graph → Delegated:
   - Chat.ReadWrite
   - ChannelMessage.Send
   - Calendars.ReadWrite
   - User.Read
9. Click Grant admin consent
10. Put the three values in .env:
    TEAMS_CLIENT_ID=...
    TEAMS_TENANT_ID=...
    TEAMS_CLIENT_SECRET=...

---

## BABY STEP 7 — Test Teams Connection
Goal: Send a test message to yourself in Teams.

1. In main.py menu, choose the Teams test option
2. If you receive the test message in Teams → Teams is working ✅
3. Mark ✅ Microsoft Teams in docs/setup-status.md

---

## BABY STEP 8 — First Real Task
Goal: Categorise your actual inbox.

1. In main.py menu, choose option 1 (Process & Categorise Emails)
2. Watch the agent read emails and apply labels
3. Open Gmail — you should see HR/ labels applied
4. Save any observations to memory.md

---

## BABY STEP 9 — Draft Your First Reply
Goal: Let the agent suggest a reply to a real email.

1. Choose option 2 (Draft Email Reply)
2. Pick an email you need to respond to
3. Review the draft — edit if needed — save to Gmail drafts
4. Note: the draft is NOT sent until you send it manually from Gmail

---

## BABY STEP 10 — Generate Your First Document
Goal: Create an offer letter or onboarding document.

1. Choose option 5 (Generate HR Document)
2. Select Offer Letter
3. Fill in the details
4. Check output/ folder for the generated file

---

## After All 10 Steps
You have a fully functioning HR agent. Now the compounding begins:
- Every correction → add to memory.md
- Every new email pattern discovered → add to skills/email-categorisation.md
- Every API quirk → add to the relevant docs/ file
- Review memory.md weekly and prune anything outdated
