"""Microsoft Teams service via Microsoft Graph API."""

import json
import os
from pathlib import Path
import requests
import msal
from .config import (
    TEAMS_CLIENT_ID,
    TEAMS_CLIENT_SECRET,
    TEAMS_TENANT_ID,
    TEAMS_TOKEN_FILE,
    TEAMS_SCOPES,
)

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def get_teams_token() -> str:
    """
    Acquire a Microsoft Graph access token using MSAL.
    Saves the token to teams_token.json for reuse.
    Returns the access token string.
    """
    app = msal.PublicClientApplication(
        client_id=TEAMS_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TEAMS_TENANT_ID}",
    )

    # Try silent (cached) token first
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(TEAMS_SCOPES, account=accounts[0])
        if result and "access_token" in result:
            return result["access_token"]

    # Interactive login — opens browser once, saves session
    print("\n[Teams] Opening browser for Microsoft login...")
    result = app.acquire_token_interactive(scopes=TEAMS_SCOPES)

    if "access_token" not in result:
        error = result.get("error_description", str(result))
        raise RuntimeError(f"Teams authentication failed: {error}")

    return result["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def get_joined_teams(token: str) -> list[dict]:
    """Return teams the authenticated user belongs to."""
    resp = requests.get(f"{GRAPH_BASE}/me/joinedTeams", headers=_headers(token))
    resp.raise_for_status()
    return resp.json().get("value", [])


def get_team_channels(token: str, team_id: str) -> list[dict]:
    """Return channels for a given team."""
    resp = requests.get(
        f"{GRAPH_BASE}/teams/{team_id}/channels", headers=_headers(token)
    )
    resp.raise_for_status()
    return resp.json().get("value", [])


def send_channel_message(token: str, team_id: str, channel_id: str, message: str) -> dict:
    """Send a plain-text message to a Teams channel."""
    body = {"body": {"contentType": "text", "content": message}}
    resp = requests.post(
        f"{GRAPH_BASE}/teams/{team_id}/channels/{channel_id}/messages",
        headers=_headers(token),
        json=body,
    )
    resp.raise_for_status()
    return resp.json()


def get_or_create_chat(token: str, recipient_email: str) -> str:
    """Get existing 1:1 chat ID with recipient, or create one. Returns chat_id."""
    # List existing chats and look for one with only this user
    me_resp = requests.get(f"{GRAPH_BASE}/me", headers=_headers(token))
    me_resp.raise_for_status()
    my_id = me_resp.json()["id"]

    # Search for existing 1:1 chat
    chats_resp = requests.get(
        f"{GRAPH_BASE}/me/chats?$expand=members", headers=_headers(token)
    )
    chats_resp.raise_for_status()
    for chat in chats_resp.json().get("value", []):
        if chat.get("chatType") == "oneOnOne":
            members = chat.get("members", [])
            emails = [m.get("email", "").lower() for m in members]
            if recipient_email.lower() in emails:
                return chat["id"]

    # Create new 1:1 chat
    body = {
        "chatType": "oneOnOne",
        "members": [
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "roles": ["owner"],
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users/{my_id}",
            },
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "roles": ["owner"],
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{recipient_email}')",
            },
        ],
    }
    create_resp = requests.post(
        f"{GRAPH_BASE}/chats", headers=_headers(token), json=body
    )
    create_resp.raise_for_status()
    return create_resp.json()["id"]


def send_direct_message(token: str, recipient_email: str, message: str) -> dict:
    """Send a direct 1:1 Teams message to a user by email."""
    chat_id = get_or_create_chat(token, recipient_email)
    body = {"body": {"contentType": "text", "content": message}}
    resp = requests.post(
        f"{GRAPH_BASE}/chats/{chat_id}/messages",
        headers=_headers(token),
        json=body,
    )
    resp.raise_for_status()
    return resp.json()


def create_teams_meeting(
    token: str,
    title: str,
    start_datetime: str,
    end_datetime: str,
    attendees: list[str],
    description: str = "",
) -> dict:
    """
    Create an online Teams meeting via Graph Calendar API.
    Returns the created event including the Teams join URL.
    """
    body = {
        "subject": title,
        "body": {"contentType": "text", "content": description},
        "start": {"dateTime": start_datetime, "timeZone": "UTC"},
        "end": {"dateTime": end_datetime, "timeZone": "UTC"},
        "isOnlineMeeting": True,
        "onlineMeetingProvider": "teamsForBusiness",
        "attendees": [
            {
                "emailAddress": {"address": email},
                "type": "required",
            }
            for email in attendees
        ],
    }
    resp = requests.post(
        f"{GRAPH_BASE}/me/events", headers=_headers(token), json=body
    )
    resp.raise_for_status()
    return resp.json()
