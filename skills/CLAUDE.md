# HR Task Skills — Quick Reference

This folder contains **task-specific how-to guides**. Each skill describes a discrete HR workflow.

## Skills Overview

| Skill | When to Use | Trigger Keywords |
|-------|-------------|-----------------|
| [email-categorisation.md](email-categorisation.md) | Reading & sorting emails | "categorize email", "sort inbox", "label" |
| [reply-drafting.md](reply-drafting.md) | Writing HR responses | "draft reply", "respond to", "write email" |
| [document-drafting.md](document-drafting.md) | Creating HR docs | "draft contract", "create document", "generate" |
| [calendar-events.md](calendar-events.md) | Scheduling meetings | "schedule meeting", "create event", "add to calendar" |
| [teams-messaging.md](teams-messaging.md) | Teams communication | "send to teams", "teams message", "notify team" |

## How Skills Are Organized

Each skill file has:
- **Trigger phrase** — Keywords that activate this skill
- **Prerequisites** — What to check before using
- **Steps** — Numbered instructions
- **API reference** — Which service module to use
- **Examples** — Real usage examples
- **Approval gate** — Who needs to approve first

## Important Pattern: Always Preview

Every skill that writes/sends requires approval:
1. Generate preview
2. Show user
3. Get explicit approval
4. Execute

**Never send/write without approval.**

## Common Skill Combinations

### Onboarding a new employee
1. Use [document-drafting.md](document-drafting.md) → draft contract
2. Use [reply-drafting.md](reply-drafting.md) → welcome email
3. Use [calendar-events.md](calendar-events.md) → schedule day-01 meeting
4. Use [teams-messaging.md](teams-messaging.md) → notify team

### Handling employee inquiry
1. Use [email-categorisation.md](email-categorisation.md) → classify email
2. Use [reply-drafting.md](reply-drafting.md) → draft response
3. Preview and get approval
4. Send using email_service.py

### Scheduling all-hands meeting
1. Use [calendar-events.md](calendar-events.md) → create event
2. Use [teams-messaging.md](teams-messaging.md) → announce to team
3. Get attendee confirmation

## When NOT to Use Skills

- **For data operations:** Use fetch_sheets_data.py directly
- **For payroll:** Go to payroll/ folder (isolation rule)
- **For debugging:** Use hr_assistant/ service modules
- **For one-off scripts:** Create in root directory

## Adding a New Skill

If you're creating a new HR workflow:
1. Create `skills/new-workflow-name.md`
2. Follow the template in [email-categorisation.md](email-categorisation.md)
3. Include: trigger, prerequisites, steps, API reference, approval gate
4. Update this CLAUDE.md with the new skill
5. Document in root CLAUDE.md → Skills section

---
**Last updated:** 2026-05-12  
**Total skills:** 5  
**All skills:** Require preview + approval before execution
