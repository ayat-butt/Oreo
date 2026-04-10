#!/usr/bin/env python3
"""HR Assistant — main CLI entry point."""

import sys
from datetime import datetime, timedelta
from hr_assistant.config import get_google_services, COMPANY_NAME
from hr_assistant import gmail_service, calendar_service, drive_service, claude_assistant


def print_header(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_email(email: dict, idx: int) -> None:
    print(f"\n[{idx}] From: {email['sender']}")
    print(f"     Subject: {email['subject']}")
    print(f"     Date: {email['date'][:25]}")
    print(f"     Preview: {email['snippet'][:100]}...")


def menu_process_emails(services: dict) -> None:
    """Fetch unread emails, categorize with Claude, and apply Gmail labels."""
    print_header("Process & Categorize Emails")

    gmail = services["gmail"]
    label_map = gmail_service.ensure_hr_labels(gmail)

    print("\nFetching unread emails...")
    emails = gmail_service.get_unread_emails(gmail, max_results=10)

    if not emails:
        print("No unread emails found.")
        return

    print(f"\nFound {len(emails)} unread email(s).\n")

    for i, email in enumerate(emails):
        print_email(email, i + 1)

        print("  Categorizing with Claude...", end=" ", flush=True)
        result = claude_assistant.categorize_email(
            email["subject"], email["body"], email["sender"]
        )
        category = result["category"]
        priority = result["priority"]
        reason = result["reason"]
        print(f"Done.")
        print(f"  → Category: {category}  |  Priority: {priority}")
        print(f"  → Reason: {reason}")

        label_id = label_map.get(category)
        if label_id:
            gmail_service.apply_label(gmail, email["id"], label_id)
            print(f"  ✓ Label '{category}' applied.")

    print("\n✓ All emails categorized.")


def menu_draft_reply(services: dict) -> None:
    """Select an email and get Claude to draft a reply."""
    print_header("Draft Email Reply")

    gmail = services["gmail"]
    emails = gmail_service.get_unread_emails(gmail, max_results=10)

    if not emails:
        print("No unread emails found.")
        return

    for i, email in enumerate(emails):
        print_email(email, i + 1)

    try:
        choice = int(input("\nSelect email number to draft reply for: ")) - 1
        if not 0 <= choice < len(emails):
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input.")
        return

    email = emails[choice]
    print("\nCategorizing email...", end=" ", flush=True)
    cat_result = claude_assistant.categorize_email(
        email["subject"], email["body"], email["sender"]
    )
    category = cat_result["category"]
    print(f"{category}")

    print("Drafting reply with Claude...", end=" ", flush=True)
    reply_text = claude_assistant.draft_reply(
        email["subject"], email["body"], email["sender"], category
    )
    print("Done.\n")

    print("--- DRAFTED REPLY ---")
    print(reply_text)
    print("---------------------")

    action = input("\n[S]ave as draft / [E]nter to discard: ").strip().upper()
    if action == "S":
        draft = gmail_service.create_draft(
            gmail,
            to=email["sender"],
            subject=email["subject"],
            body=reply_text,
            thread_id=email["thread_id"],
        )
        print(f"✓ Draft saved (ID: {draft['id']})")


def menu_create_calendar_event(services: dict) -> None:
    """Extract event from an email or create one manually."""
    print_header("Create Calendar Event")

    print("\n1. Extract event from email")
    print("2. Create event manually")
    choice = input("\nSelect option: ").strip()

    calendar = services["calendar"]

    if choice == "1":
        gmail = services["gmail"]
        emails = gmail_service.get_unread_emails(gmail, max_results=10)

        if not emails:
            print("No unread emails.")
            return

        for i, email in enumerate(emails):
            print_email(email, i + 1)

        try:
            idx = int(input("\nSelect email number: ")) - 1
            if not 0 <= idx < len(emails):
                print("Invalid selection.")
                return
        except ValueError:
            print("Invalid input.")
            return

        email = emails[idx]
        print("Extracting event details with Claude...", end=" ", flush=True)
        event_data = claude_assistant.extract_calendar_event(
            email["subject"], email["body"]
        )
        print("Done.")

        if not event_data:
            print("No event/meeting detected in this email.")
            return

        print(f"\nEvent detected:")
        print(f"  Title: {event_data['title']}")
        print(f"  Date: {event_data['date']}  Time: {event_data['time']}")
        print(f"  Duration: {event_data.get('duration_minutes', 60)} min")
        print(f"  Location: {event_data.get('location', '')}")
        print(f"  Attendees: {', '.join(event_data.get('attendees', []))}")

        if event_data["date"] == "unspecified":
            event_data["date"] = input("Enter date (YYYY-MM-DD): ").strip()
        if event_data["time"] == "unspecified":
            event_data["time"] = input("Enter time (HH:MM, 24h): ").strip()

        confirm = input("\nCreate this event? [y/N]: ").strip().lower()
        if confirm != "y":
            return

        start_dt = f"{event_data['date']}T{event_data['time']}:00"
        duration = int(event_data.get("duration_minutes", 60))
        start = datetime.fromisoformat(start_dt)
        end_dt = (start + timedelta(minutes=duration)).isoformat()

        created = calendar_service.create_event(
            calendar,
            title=event_data["title"],
            description=event_data.get("description", ""),
            start_datetime=start_dt,
            end_datetime=end_dt,
            attendees=event_data.get("attendees", []),
            location=event_data.get("location", ""),
        )
        print(f"\n✓ Event created: {created.get('htmlLink', created['id'])}")

    elif choice == "2":
        title = input("Event title: ").strip()
        description = input("Description: ").strip()
        date = input("Date (YYYY-MM-DD): ").strip()
        time = input("Start time (HH:MM, 24h): ").strip()
        duration = input("Duration in minutes [60]: ").strip() or "60"
        attendees_raw = input("Attendee emails (comma-separated, or blank): ").strip()
        location = input("Location (or blank): ").strip()

        attendees = [a.strip() for a in attendees_raw.split(",") if a.strip()]
        start_dt = f"{date}T{time}:00"
        start = datetime.fromisoformat(start_dt)
        end_dt = (start + timedelta(minutes=int(duration))).isoformat()

        created = calendar_service.create_event(
            calendar,
            title=title,
            description=description,
            start_datetime=start_dt,
            end_datetime=end_dt,
            attendees=attendees,
            location=location,
        )
        print(f"\n✓ Event created: {created.get('htmlLink', created['id'])}")


def menu_view_calendar(services: dict) -> None:
    """Show upcoming calendar events."""
    print_header("Upcoming Calendar Events")
    days = input("\nShow events for next how many days? [7]: ").strip() or "7"
    events = calendar_service.list_upcoming_events(services["calendar"], days=int(days))
    print(f"\nUpcoming events (next {days} days):\n")
    print(calendar_service.format_event_summary(events))


def menu_generate_document(services: dict) -> None:
    """Generate an HR document using Claude and save to Google Drive."""
    print_header("Generate HR Document")

    print("\nDocument types:")
    print("  1. Offer Letter")
    print("  2. Onboarding Welcome")
    print("  3. Employment Contract")
    print("  4. Policy Update")
    print("  5. Custom Document")

    type_map = {
        "1": "offer_letter",
        "2": "onboarding",
        "3": "contract",
        "4": "policy_update",
        "5": "custom",
    }
    choice = input("\nSelect type: ").strip()
    doc_type = type_map.get(choice, "custom")

    print("\nProvide document details (press Enter to skip optional fields):")
    details: dict = {}

    if doc_type in ("offer_letter", "onboarding", "contract"):
        details["employee_name"] = input("Employee name: ").strip()
        details["position"] = input("Job title/position: ").strip()
        details["start_date"] = input("Start date (YYYY-MM-DD): ").strip()

    if doc_type in ("offer_letter", "contract"):
        details["salary"] = input("Annual salary (e.g. $75,000): ").strip()
        details["department"] = input("Department: ").strip()
        details["manager"] = input("Reporting manager: ").strip()

    if doc_type == "policy_update":
        details["policy_name"] = input("Policy name: ").strip()
        details["effective_date"] = input("Effective date: ").strip()
        details["summary"] = input("Brief policy summary: ").strip()

    if doc_type == "custom":
        details["description"] = input("Describe what this document should contain: ").strip()

    print("\nGenerating document with Claude...", end=" ", flush=True)
    doc_result = claude_assistant.generate_hr_document(doc_type, details)
    print("Done.")

    print(f"\n--- DOCUMENT PREVIEW ---")
    print(doc_result["content"][:500] + "..." if len(doc_result["content"]) > 500 else doc_result["content"])
    print("------------------------")

    save = input("\n[S]ave to Google Drive / [P]rint full / [D]iscard: ").strip().upper()

    if save == "P":
        print("\n--- FULL DOCUMENT ---")
        print(doc_result["content"])
        print("---------------------")
        save = input("\n[S]ave to Google Drive / [D]iscard: ").strip().upper()

    if save == "S":
        print("Saving to Google Drive...", end=" ", flush=True)
        doc_meta = drive_service.create_document(
            services["docs"],
            services["drive"],
            title=doc_result["title"],
            content=doc_result["content"],
        )
        print("Done.")
        print(f"\n✓ Document saved: {doc_meta['url']}")


def menu_view_documents(services: dict) -> None:
    """List recent HR documents in Google Drive."""
    print_header("HR Documents in Google Drive")
    docs_list = drive_service.list_hr_documents(services["drive"])
    print("\nRecent documents:\n")
    print(drive_service.format_document_list(docs_list))


def menu_email_briefing(services: dict) -> None:
    """Generate a Claude-powered summary of current inbox."""
    print_header("Email Briefing Summary")
    gmail = services["gmail"]
    print("\nFetching emails...", end=" ", flush=True)
    emails = gmail_service.get_unread_emails(gmail, max_results=15)
    print(f"Found {len(emails)} emails.")

    if not emails:
        print("Inbox is clear!")
        return

    print("Generating briefing with Claude...", end=" ", flush=True)
    summary = claude_assistant.summarize_email_batch(emails)
    print("Done.\n")
    print(summary)


def main() -> None:
    print(f"\n{'*'*60}")
    print(f"  HR Assistant — {COMPANY_NAME}")
    print(f"  Powered by Claude + Google Workspace")
    print(f"{'*'*60}")

    print("\nConnecting to Google Workspace...", end=" ", flush=True)
    try:
        services = get_google_services()
        print("Connected.\n")
    except FileNotFoundError as e:
        print(f"\n✗ {e}")
        sys.exit(1)

    menu_options = {
        "1": ("Process & Categorize Emails", menu_process_emails),
        "2": ("Draft Email Reply", menu_draft_reply),
        "3": ("Create Calendar Event", menu_create_calendar_event),
        "4": ("View Upcoming Events", menu_view_calendar),
        "5": ("Generate HR Document", menu_generate_document),
        "6": ("View HR Documents in Drive", menu_view_documents),
        "7": ("Email Briefing Summary", menu_email_briefing),
        "q": ("Quit", None),
    }

    while True:
        print("\n--- MAIN MENU ---")
        for key, (label, _) in menu_options.items():
            print(f"  {key}. {label}")

        choice = input("\nSelect option: ").strip().lower()

        if choice == "q":
            print("\nGoodbye!")
            break

        if choice not in menu_options:
            print("Invalid option.")
            continue

        _, handler = menu_options[choice]
        if handler:
            try:
                handler(services)
            except KeyboardInterrupt:
                print("\n(Cancelled)")
            except Exception as e:
                print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()
