# Skill: Email Categorisation

## Metadata
- **Trigger Phrases:** "categorize email", "sort inbox", "label emails", "organize email"
- **Input Files:** 4 files total (~200 lines)
- **Output Location:** output/email/categorised/[YYYY-MM-DD]/
- **Dependencies:** Gmail API connected
- **Execution Time:** ~2 minutes per 50 emails
- **Approval Required:** Yes (preview before applying labels)

## Input Files (Exact)
1. `skills/email-categorisation.md` (this file)
2. `memory/MEMORY.md` (email-related sections)
3. `memory/feedback_email_*.md` (email rules, ~2-3 files)
4. `docs/gmail-api-reference.md` (Gmail API patterns)

**Files NOT Loaded:**
- ❌ Payroll files
- ❌ Contract files
- ❌ Calendar files
- ❌ Teams files

## Execution Flow
```
User: "Categorize my emails"
  ↓
Check: Gmail API connected? (docs/setup-status.md)
Check: Credentials valid? (token.json exists)
Check: Output folder ready? (output/email/categorised/)
  ↓
Load: 4 input files above
  ↓
Execute:
  1. Fetch max 20 unread emails
  2. For each email: determine label
  3. Apply label via Gmail API
  4. Log result
  ↓
Output: output/email/categorised/[date]/results.md
  ↓
Verify: All emails processed
Confirm: Show preview to user
Action: Apply on approval
```

## Purpose
Read unread Gmail messages and apply one of four HR labels automatically.

## Labels
| Label                  | Trigger keywords |
|------------------------|-----------------|
| HR/Contracts           | contract, offer letter, agreement, NDA, sign, new hire, onboarding, employment, terms |
| HR/Benefits            | benefit, health insurance, dental, vision, 401k, retirement, PTO, vacation, leave, wellness |
| HR/Payroll             | payroll, salary, pay, paycheck, direct deposit, tax, W-2, compensation, bonus, raise |
| HR/Employee-Queries    | question, query, help, policy, procedure, request, complaint, feedback, concern, HR |

## Instructions
1. Fetch unread emails from inbox (max 20 at a time).
2. For each email, pass subject + first 500 characters of body to Claude.
3. Ask Claude: "Which single HR label fits best? Return JSON: {category, priority, reason}."
4. Apply the returned label via Gmail API modify endpoint.
5. Log the result: date, sender, subject, label applied.
6. Save any new keyword patterns discovered to memory.md.

## Priority Rules
- high   → legal/contract deadlines, payroll errors, compliance issues
- medium → benefit enrolment, general queries with deadlines
- low    → routine questions, informational requests

## Common Mistakes
- Guessing label from subject alone: always include body snippet in prompt.
- Applying multiple labels: apply exactly ONE label per email.
- Skipping logging: always log what was labelled and why.

## Output Format
```
[YYYY-MM-DD HH:MM] Labelled email
  From:     sender@example.com
  Subject:  Re: Employment Contract
  Label:    HR/Contracts  |  Priority: high
  Reason:   Contains word "contract" and "sign by"
```
