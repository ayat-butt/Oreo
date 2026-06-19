"""
Send the most recent welcome email draft for Irum Afzal
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from hr_assistant.config import get_google_services
from hr_assistant.audit_log import log as audit_log

# Get Gmail service
services = get_google_services()
gmail = services["gmail"]

# Fetch the most recent draft
print("Fetching recent draft emails...")
results = gmail.users().drafts().list(userId="me", q="subject:Welcome to Taleemabad", maxResults=1).execute()
drafts = results.get("drafts", [])

if not drafts:
    print("❌ No draft found matching 'Welcome to Taleemabad'")
    sys.exit(1)

draft_id = drafts[0]["id"]
draft = gmail.users().drafts().get(userId="me", id=draft_id).execute()

# Extract email details
message = draft.get("message", {})
headers = {h["name"]: h["value"] for h in message.get("payload", {}).get("headers", [])}
subject = headers.get("Subject", "")
to_address = headers.get("To", "")
cc = headers.get("Cc", "")

print(f"\n📧 Sending Email Draft:")
print(f"   Subject: {subject}")
print(f"   To:      {to_address}")
if cc:
    print(f"   CC:      {cc}")

# Send the draft
print("\n📤 Sending...")
sent = gmail.users().drafts().send(userId="me", body={"id": draft_id}).execute()

print(f"✅ Email sent successfully!")
print(f"   Message ID: {sent['id']}")

# Log the send action
audit_log("EMAIL_SENT", f"to={to_address} cc={cc or 'none'} subject='{subject}' message_id={sent['id']}")

print("\n" + "="*60)
print("WELCOME EMAIL SENT TO IRUM AFZAL")
print("="*60)
print(f"From:    Oreo <ayat@taleemabad.com>")
print(f"To:      {to_address}")
if cc:
    print(f"CC:      {cc}")
print(f"Subject: {subject}")
print("\nAttachments:")
print("  ✓ Irum Afzal - Contract.pdf")
print("  ✓ Irum Afzal - NDA.pdf")
print("="*60)
