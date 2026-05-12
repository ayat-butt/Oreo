# Skill: Reply Drafting

## Metadata
- **Trigger Phrases:** "draft reply", "respond to", "write email response", "reply to email"
- **Input Files:** 5 files total (~300 lines)
- **Output Location:** output/replies/[YYYY-MM-DD]/
- **Dependencies:** Gmail API connected, Claude API available
- **Execution Time:** ~5 minutes per reply
- **Approval Required:** Yes (always preview before saving draft)

## Input Files (Exact)
1. `skills/reply-drafting.md` (this file)
2. `memory/MEMORY.md` (email-related sections)
3. `memory/feedback_email_*.md` (email rules, ~2 files)
4. `memory/feedback_email_formatting.md` (formatting standards)
5. `memory/feedback_oreo_signature.md` (signature rules)

**Files NOT Loaded:**
- ❌ Payroll files
- ❌ Contract files
- ❌ Calendar files
- ❌ Teams files

## Execution Flow
```
User: "Draft a reply to this email"
  ↓
Check: Gmail API connected? (docs/setup-status.md)
Check: Claude API available?
Check: Output folder ready? (output/replies/)
  ↓
Load: 5 input files above
  ↓
Execute:
  1. Show original email to user
  2. Generate draft reply
  3. Display preview
  4. Get approval
  5. Save as Gmail draft
  6. Log output
  ↓
Output: output/replies/[date]/draft_[timestamp].md
  ↓
Verify: Draft created in Gmail
Confirm: Show link to user
```

## Purpose
Draft professional HR email replies using Claude, then save as Gmail drafts for human review before sending.

## Instructions
1. Show the user the original email (sender, subject, body).
2. Ask Claude to draft a reply. Include in the prompt:
   - The email category (from categorisation step)
   - The full original body (up to 2000 chars)
   - Instruction: "Professional HR tone, under 200 words, end with Best regards / HR Team"
3. Display the draft to the user for review.
4. Offer three options: [S]ave as draft / [E]dit / [D]iscard
5. If saving: call Gmail drafts.create API with thread_id to keep thread intact.
6. NEVER send automatically — always save as draft first.

## Tone Guidelines by Category
| Category              | Tone |
|-----------------------|------|
| HR/Contracts          | Formal, precise, deadline-aware |
| HR/Benefits           | Warm, informative, include next steps |
| HR/Payroll            | Calm, factual, reassuring |
| HR/Employee-Queries   | Empathetic, helpful, action-oriented |

## Template Endings
Always close with:
```
Best regards,
[HR Manager Name]
HR Team, [COMPANY_NAME]
```

## Common Mistakes
- Sending directly without human review: ALWAYS save as draft.
- Generic replies that don't reference the sender's specific issue.
- Missing next steps: every reply should tell the sender what happens next.
