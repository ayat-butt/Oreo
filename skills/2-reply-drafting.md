# Skill 2: Reply Drafting

## Metadata
- **Trigger Phrases:** "draft reply", "respond to", "write email response", "reply to email", "draft response"
- **Input Files:** 5 files total (~300 lines)
- **Output Location:** output/replies/[YYYY-MM-DD]/
- **Dependencies:** Gmail API connected, Claude API available, Anthropic key in .env
- **Execution Time:** ~5 minutes per reply
- **Approval Required:** YES — Always preview before saving as draft

## Input Files (Exact)
1. `skills/2-reply-drafting.md` (this file)
2. `memory/MEMORY.md` (email-related sections)
3. `memory/feedback_email_*.md` (email rules, ~2-3 files)
4. `memory/feedback_oreo_signature.md` (Oreo signature rules)
5. Original email content (provided by user)

**Files NOT Loaded:**
- ❌ Payroll files
- ❌ Contract files
- ❌ Calendar files
- ❌ Teams files
- ❌ Probation files

## Execution Flow
```
User: "Draft a reply to this email: [original email]"
  ↓
Check: Gmail API connected? (docs/setup-status.md)
Check: Claude API available? (ANTHROPIC_API_KEY in .env)
Check: Output folder ready? (output/replies/)
  ↓
Load: 5 input files above
Load: Original email content from user
  ↓
Execute:
  1. Show original email to user (sender, subject, body)
  2. Determine email category (HR/Contracts, HR/Benefits, etc.)
  3. Extract key points from original email
  4. Generate draft reply using Claude
  5. Display preview to user
  6. Get approval: [S]ave as draft / [E]dit / [D]iscard
  7. Save as Gmail draft (if approved)
  8. Log output
  ↓
Output: output/replies/[date]/draft_[timestamp].md
  ↓
Verify: Draft created in Gmail
Confirm: Show link to user
```

## Purpose
Draft professional HR email replies using Claude AI, then save as Gmail drafts for human review before sending. Replies use proper tone based on email category and Oreo signature.

## Mandatory Rules (LOCKED)

### Rule 1: Always Show Original Email First
Before drafting:
- Show sender, subject, full body
- Ask user to confirm this is the email to reply to
- Example:
  ```
  Original email from: john@example.com
  Subject: Re: Salary Adjustment
  Body: [show full content]
  
  Is this the email you want to reply to? [Y/N]
  ```

### Rule 2: Tone Guidelines by Category (EXACT)
| Category | Tone | Word Count | Ending |
|----------|------|-----------|--------|
| HR/Contracts | Formal, precise, deadline-aware | Under 300 words | "Best regards, [HR Manager], HR Team, Taleemabad" |
| HR/Benefits | Warm, informative, include next steps | Under 250 words | "Best regards, Oreo — HR Assistant" |
| HR/Payroll | Calm, factual, reassuring | Under 200 words | "Best regards, [HR Manager], HR Team, Taleemabad" |
| HR/Employee-Queries | Empathetic, helpful, action-oriented | Under 200 words | "Best regards, Oreo — Ayat's Personal AI Assistant" |

### Rule 3: Oreo Signature Rules (LOCKED)
- **For HR Queries:** "Best regards, Oreo — Ayat's Personal AI Assistant"
- **For Official HR:** "Best regards, [HR Manager Name], HR Team, Taleemabad"
- **For Contracts:** Always sign as HR Team with manager name
- **For Benefits:** Warm, can use Oreo signature if friendly tone
- **Check memory:** Read memory/feedback_oreo_signature.md for exact rules

### Rule 4: Reference Sender's Specific Issue
- Never generic replies: "Thank you for your email"
- Always reference: "Thank you for asking about your salary adjustment"
- Show you read and understood their concern
- Acknowledge specific details (name, date, amount if applicable)

### Rule 5: Include Next Steps
Every reply must tell sender:
- What happens next
- When to expect updates
- Who to contact with questions
- Example: "I'll review your request and send you an update by Friday."

### Rule 6: Preview Before Saving
- Display draft to user for review
- Show: sender, subject, full draft body, signature
- Get explicit approval: [S]ave as draft / [E]dit / [D]iscard
- Never auto-save without approval

### Rule 7: Never Send Directly (LOCKED)
- Always save as DRAFT first
- User must review in Gmail before sending
- Prevents accidental sends of unvetted replies
- Rule is non-negotiable

### Rule 8: Keep Thread Intact
- Link reply to original email thread_id
- Gmail draft stays in same thread
- User can see full conversation context
- Use Gmail API: save as draft with thread_id

## Claude Prompt Template (LOCKED)

```
Original email from: [SENDER]
Subject: [SUBJECT]
Body: [FULL BODY]

Email category: [HR/Contracts | HR/Benefits | HR/Payroll | HR/Employee-Queries]

Draft a professional reply using this tone:
- Tone: [Formal/Warm/Calm/Empathetic]
- Word count: [Under 200-300 words depending on category]
- Reference their specific issue (don't be generic)
- Include next steps: what happens now
- Sign off with: "Best regards, [signature from memory]"

Requirements:
1. Acknowledge their specific concern
2. Provide clear answer or next steps
3. Be professional and warm (as appropriate)
4. Include contact info for follow-up
5. Sign with Oreo or HR Team (per rules)

Return ONLY the email body (no subject, no sender).
```

## Common Mistakes (LOCKED)

❌ **Mistake 1: Sending Directly Without Human Review**
- ALWAYS save as draft first
- User must review in Gmail
- Never use "send now" — only drafts allowed

❌ **Mistake 2: Generic Replies That Don't Reference Sender**
- "Thank you for your email" is too generic
- Reference their specific issue: "Thank you for asking about your salary adjustment"
- Show you read and understood

❌ **Mistake 3: Forgetting Next Steps**
- Every reply must say what happens next
- Example: "I'll send you the documents by Friday" or "Please wait for HR's approval"
- Sender needs to know what to expect

❌ **Mistake 4: Wrong Signature**
- Check memory/feedback_oreo_signature.md for rules
- Contracts usually sign as HR Team + manager name
- Queries often sign as Oreo (friendlier)
- Read the rules before drafting

❌ **Mistake 5: Skipping Thread Link**
- Draft must be linked to original email thread
- Use Gmail API with thread_id
- Keeps conversation context intact
- User sees full thread in Gmail draft

❌ **Mistake 6: Exceeding Word Count**
- Contracts: under 300 words
- Benefits/Payroll/Queries: under 200 words
- Concise is better
- If too long, condense or split into follow-up email

❌ **Mistake 7: Not Showing Original Email**
- Always show sender, subject, body first
- Confirm this is the email to reply to
- Prevents replying to wrong email

## Output Format (LOCKED)

**File:** output/replies/[YYYY-MM-DD]/draft_[timestamp].md

```
# Email Draft Reply
**Date:** 2026-05-12  
**Time:** 15:20:03 UTC  
**Status:** Saved as Gmail Draft

---

## Original Email
**From:** john.smith@example.com  
**Subject:** Re: Salary Adjustment Request  
**Body:**
[Original email body quoted]

---

## Draft Reply
**To:** john.smith@example.com  
**Category:** HR/Payroll  
**Tone:** Calm, reassuring  

**Body:**
Dear John,

Thank you for reaching out about your salary adjustment. I understand this is important to you.

I've reviewed your request and cross-checked our records. Your adjustment is in process and should be reflected in your next paycheck on [DATE]. You'll receive a confirmation email by [DATE] with all details.

If you have any questions in the meantime, please don't hesitate to reach out.

Best regards,  
Oreo — Ayat's Personal AI Assistant  
HR Team, Taleemabad

---

## Metadata
- **User Approval:** YES
- **Gmail Draft:** Created (draft_id: xxxxx)
- **Thread Link:** Yes (thread_id: xxxxx)
- **Next Steps:** User will review in Gmail and decide to send or edit

---

## Confirmation
✓ Draft reply created
  To: john.smith@example.com
  Subject: Re: Salary Adjustment Request
  Type: Gmail Draft (not sent)
  Preview: [First 100 chars]...
  
  Action: User will review in Gmail drafts and send manually
```

## Instructions — Step by Step

1. **Show Original Email**
   ```
   Original email from: john@example.com
   Subject: Salary Adjustment Request
   Body: [show full content]
   
   Is this correct? [Y/N]
   ```

2. **Determine Category**
   - Ask user or infer from keywords
   - Options: HR/Contracts, HR/Benefits, HR/Payroll, HR/Employee-Queries

3. **Draft Reply Using Claude**
   - Use template above
   - Include original email + category + tone
   - Call Claude API with prompt

4. **Display Preview**
   ```
   Draft reply:
   
   Dear John,
   
   Thank you for your salary adjustment request...
   [show full draft]
   
   Best regards, Oreo — Ayat's Personal AI Assistant
   ```

5. **Get Approval**
   ```
   Review complete? 
   [S]ave as draft / [E]dit / [D]iscard
   ```

6. **Save as Gmail Draft**
   ```python
   gmail_service.users().drafts().create(
       userId='me',
       body={
           'message': {
               'threadId': thread_id,
               'to': recipient,
               'subject': original_subject,
               'mimeType': 'text/plain',
               'body': reply_body
           }
       }
   ).execute()
   ```

7. **Log to Output**
   - Save draft details to output/replies/[date]/
   - Include original + draft + approval

8. **Confirm to User**
   ```
   ✓ Draft reply created and saved to Gmail
   To: john@example.com
   Subject: Re: Salary Adjustment Request
   Status: Gmail Draft (not sent)
   
   Action: Open Gmail drafts to send or edit
   ```

---

**Skill Status:** ✅ ACTIVE  
**Integration:** ✅ Gmail + Claude API  
**Approval Required:** YES (always save as draft)  
**Direct Send:** ❌ NEVER (always draft first)  
**Data Safety:** User controls when/if draft is sent
