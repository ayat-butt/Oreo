# Skill 1: Email Categorisation

## Metadata
- **Trigger Phrases:** "categorize email", "sort inbox", "label emails", "organize email", "organize emails"
- **Input Files:** 4 files total (~200 lines)
- **Output Location:** output/email/categorised/[YYYY-MM-DD]/
- **Dependencies:** Gmail API connected
- **Execution Time:** ~2 minutes per 50 emails
- **Approval Required:** YES — Always preview labels before applying

## Input Files (Exact)
1. `skills/1-email-categorisation.md` (this file)
2. `memory/MEMORY.md` (email-related sections)
3. `memory/feedback_email_*.md` (email rules, ~2-3 files)
4. `docs/gmail-api-reference.md` (Gmail API patterns)

**Files NOT Loaded:**
- ❌ Payroll files
- ❌ Contract files
- ❌ Calendar files
- ❌ Teams files
- ❌ Probation files

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
  2. For each email: READ subject + first 500 chars of body
  3. Pass to Claude with: "Which single HR label fits best?"
  4. Claude returns: {category, priority, reason}
  5. Apply label via Gmail API modify endpoint
  6. Log result with: date, sender, subject, label, reason
  ↓
Output: output/email/categorised/[date]/results.md
  ↓
Verify: All emails processed (count check)
Confirm: Show preview to user with summary
Action: Apply on approval [Y/N]
```

## Purpose
Read unread Gmail messages and apply one of four HR labels automatically using Claude AI.

## Label Categories (LOCKED)

| Label | Trigger Keywords | Priority Rules | Action |
|-------|---|---|---|
| **HR/Contracts** | contract, offer letter, agreement, NDA, sign, new hire, onboarding, employment, terms | high=legal/contract deadlines, medium=standard terms | Legal review, signature needed |
| **HR/Benefits** | benefit, health insurance, dental, vision, 401k, retirement, PTO, vacation, leave, wellness | medium=enrolment, low=informational | Enrolment deadline tracking |
| **HR/Payroll** | payroll, salary, pay, paycheck, direct deposit, tax, W-2, compensation, bonus, raise | high=errors/compliance, medium=queries | Escalate to payroll team |
| **HR/Employee-Queries** | question, query, help, policy, procedure, request, complaint, feedback, concern, HR | medium=deadlines, low=routine | Draft reply within 24h |

## Mandatory Rules (LOCKED)

### Rule 1: Read BEFORE Categorizing
- **Always read** subject + first 500 characters of body
- **Never guess** from subject alone
- **Include full context** in Claude prompt
- **Verify keywords** match the email body intent

### Rule 2: Apply Exactly ONE Label
- Each email gets ONE label only
- If torn between two: choose the more urgent
- If still unsure: ask user, don't guess
- Never apply multiple labels to same email

### Rule 3: Priority Assignment
| Priority | Condition | Example |
|----------|-----------|---------|
| high | Legal deadlines, contract expiry, payroll errors, compliance issues | "Contract must be signed by Friday" |
| medium | Benefit enrolment with deadline, queries with urgency | "Please enrol by month-end" |
| low | Routine questions, informational, no deadline | "What is the PTO policy?" |

### Rule 4: Always Log Results
Format:
```
[YYYY-MM-DD HH:MM] Labelled email
  From:     sender@example.com
  Subject:  Re: Employment Contract
  Label:    HR/Contracts  |  Priority: high
  Reason:   Contains "contract" and "sign by", legal deadline detected
```

### Rule 5: Save New Patterns to Memory
If email contains NEW keyword pattern not in label rules:
- Note it in output log
- Add to memory/feedback_email_keywords.md
- Update this file's trigger keywords
- Improves future categorizations

### Rule 6: Preview Before Applying Labels
- Show user ALL emails to be labelled (count, senders, subjects)
- Show user which label each email will get
- Get explicit approval: [A]pply / [R]eview each / [C]ancel
- Never apply labels without user approval

## Claude Integration (LOCKED)

When passing email to Claude:

**Prompt Template:**
```
Email subject: [SUBJECT]
Email body (first 500 chars): [BODY]

Which single HR label fits best?
- HR/Contracts (legal, contracts, onboarding)
- HR/Benefits (health, retirement, PTO, leave)
- HR/Payroll (salary, pay, tax, compensation)
- HR/Employee-Queries (questions, policies, feedback)

Return ONLY a JSON object:
{
  "category": "HR/[Label]",
  "priority": "high" | "medium" | "low",
  "reason": "Brief explanation (1 sentence)"
}
```

**Never:**
- Ask Claude to apply multiple labels
- Ask Claude for subjective opinions
- Ignore Claude's reason field
- Override Claude's choice without user confirmation

## Common Mistakes (LOCKED)

❌ **Mistake 1: Guessing Label from Subject Only**
- "Contract" in subject ≠ always HR/Contracts
- Read the body (first 500 chars) ALWAYS
- Example: "Re: Contract with IT vendor" = not HR/Contracts, ignore it

❌ **Mistake 2: Applying Multiple Labels**
- Each email = ONE label
- If unsure, ask user or Claude
- Never: "This could be benefits AND payroll"
- Pick the MOST relevant

❌ **Mistake 3: Skipping Logging**
- Log EVERY email categorized
- Include: date, sender, subject, label, reason
- Logging is not optional
- Logs go to: output/email/categorised/[date]/results.md

❌ **Mistake 4: Ignoring Claude's Reason**
- Claude provides "reason" for every label
- If reason seems wrong: ask user to confirm
- Don't override Claude without user approval
- Reason helps track pattern changes

❌ **Mistake 5: Processing Too Many at Once**
- Max 20 unread emails per run
- Prevents overwhelming preview
- User can run multiple times if needed
- Keep output manageable

❌ **Mistake 6: Not Checking Gmail API Connection**
- Always check docs/setup-status.md first
- If Gmail ⬜ Pending → stop, inform user
- If Gmail ✅ Connected → proceed
- token.json must exist

## Output Format (LOCKED)

**File:** output/email/categorised/[YYYY-MM-DD]/categorisation_[timestamp].md

```
# Email Categorisation Results
**Date:** 2026-05-12  
**Time:** 14:35:02 UTC  
**Emails Processed:** 15  
**User Approval:** YES

---

## Summary
- HR/Contracts: 3 emails
- HR/Benefits: 5 emails
- HR/Payroll: 4 emails
- HR/Employee-Queries: 3 emails

---

## Detailed Log

[2026-05-12 14:35] Labelled email
  From:     john.smith@example.com
  Subject:  Employment Contract — Please Sign
  Label:    HR/Contracts  |  Priority: high
  Reason:   Contains "contract" and "sign by Friday", legal deadline

[2026-05-12 14:36] Labelled email
  From:     benefits@example.com
  Subject:  401k Enrolment Deadline — Extended to Month-End
  Label:    HR/Benefits  |  Priority: medium
  Reason:   Contains "enrolment" and "deadline", benefit enrolment window

[2026-05-12 14:37] Labelled email
  From:     payroll@example.com
  Subject:  Salary Direct Deposit Question
  Label:    HR/Payroll  |  Priority: medium
  Reason:   Contains "salary" and "direct deposit", payroll query

---

## Labels Applied in Gmail
✓ 15 emails labelled successfully
✓ All labels visible in Gmail inbox
✓ User can review and adjust if needed
```

## Instructions — Step by Step

1. **Check Integration Status**
   ```
   Read: docs/setup-status.md
   Confirm: Gmail API = ✅ Connected
   If Pending: Inform user, stop here
   ```

2. **Fetch Unread Emails**
   ```python
   gmail_service.users().messages().list(
       userId='me',
       q='is:unread',
       maxResults=20
   ).execute()
   ```

3. **For Each Email**
   - Read subject + first 500 chars of body
   - Prepare Claude prompt (see template above)
   - Call Claude API
   - Parse response: {category, priority, reason}

4. **Build Preview**
   ```
   Emails to categorise (15 total):
   
   From: john.smith@example.com
   Subject: Employment Contract
   Proposed Label: HR/Contracts (high priority)
   Reason: Legal deadline detected
   
   [Show all 15...]
   ```

5. **Get User Approval**
   ```
   Preview shows 15 emails ready to label.
   Apply these categorisations? [A]pply / [R]eview each / [C]ancel
   ```

6. **Apply Labels via Gmail API**
   ```python
   gmail_service.users().messages().modify(
       userId='me',
       id=message_id,
       body={'addLabelIds': [label_id]}
   ).execute()
   ```

7. **Log Results**
   - Save detailed log to output folder
   - Include timestamp, all emails processed, reasons
   - Format: categorisation_[timestamp].md

8. **Confirm to User**
   ```
   ✓ Email categorisation complete
   Emails processed: 15
   HR/Contracts: 3
   HR/Benefits: 5
   HR/Payroll: 4
   HR/Employee-Queries: 3
   
   Output: output/email/categorised/2026-05-12/categorisation_143502.md
   ```

## Approval Confirmation Format (LOCKED)

```
✓ Email categorisation complete
  Processed:        15 unread emails
  HR/Contracts:     3 (legal deadlines)
  HR/Benefits:      5 (enrolments)
  HR/Payroll:       4 (salary queries)
  HR/Queries:       3 (routine)
  
  Preview reviewed: YES
  User approval:    YES
  Labels applied:   ✓
  Output logged:    ✓
```

---

**Skill Status:** ✅ ACTIVE  
**Integration:** ✅ Gmail API Connected  
**Approval Required:** YES (always preview)  
**Data Safety:** All emails unmodified, labels only  
**Reversibility:** Labels can be removed from Gmail if needed
