# Gmail API Reference

## Authentication
- Type: OAuth 2.0
- Credentials file: credentials.json (from Google Cloud Console)
- Token file: token.json (auto-generated after first login)
- Scopes needed:
  - https://www.googleapis.com/auth/gmail.modify  (read + label + draft)
  - https://www.googleapis.com/auth/gmail.send    (send emails)

## Key Endpoints Used
| Action              | API call |
|---------------------|---------|
| List messages       | users().messages().list(userId="me", q="is:unread") |
| Get message         | users().messages().get(userId="me", id=msg_id, format="full") |
| Apply label         | users().messages().modify(userId="me", id=id, body={"addLabelIds":[id]}) |
| Create draft        | users().drafts().create(userId="me", body={"message":{"raw":raw_b64}}) |
| Send message        | users().messages().send(userId="me", body={"raw":raw_b64}) |
| List labels         | users().labels().list(userId="me") |
| Create label        | users().labels().create(userId="me", body={"name": name}) |

## Message Body Encoding
- All message bodies must be base64url encoded
- Use: base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

## Getting the Text Body
The payload is recursive — parts can contain sub-parts.
Recursively walk payload["parts"] looking for mimeType == "text/plain".
Decode body["data"] with: base64.urlsafe_b64decode(data + "==")
