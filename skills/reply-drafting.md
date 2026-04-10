# Skill: Reply Drafting

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
