# Skill: Document Drafting

## Metadata
- **Trigger Phrases:** "draft contract", "create document", "generate offer letter", "onboarding email"
- **Input Files:** 8 files total (~1000 lines)
- **Output Location:** output/documents/contracts/[Employee Name]/
- **Dependencies:** Google Drive API connected, Claude API available
- **Execution Time:** ~10 minutes per document
- **Approval Required:** Yes (always preview before saving)

## Input Files (Exact)
1. `skills/document-drafting.md` (this file)
2. `memory/MEMORY.md` (core context)
3. `memory/feedback_contract_*.md` (contract rules, ~5 files)
4. `context/onboarding-roadmap.md` (onboarding procedures)
5. `draft_contract.py` (contract generation script)
6. `hr_assistant/contract_service.py` (contract service)
7. `hr_assistant/drive_service.py` (Drive storage)
8. `docs/CLAUDE.md` (company guidelines)

**Files NOT Loaded:**
- ❌ Email files
- ❌ Payroll files
- ❌ Calendar files
- ❌ Teams files

## Execution Flow
```
User: "Draft a contract for John Smith"
  ↓
Check: Google Drive API connected? (docs/setup-status.md)
Check: Draft service available?
Check: Contract templates exist?
  ↓
Load: 8 input files above
  ↓
Execute:
  1. Collect employee details
  2. Generate document
  3. Show preview
  4. Get approval
  5. Save to output/documents/contracts/[Name]/
  6. Optional: Upload to Google Drive
  ↓
Output: output/documents/contracts/[Employee]/contract_[date].docx
  ↓
Verify: File created and accessible
Confirm: Show link to user
```

## Purpose
Generate HR documents (offer letters, contracts, onboarding packs, policy updates)
using Claude and save them to the output/ folder and optionally to Google Drive.

## Document Types
| Type            | Required details |
|-----------------|-----------------|
| offer_letter    | employee_name, position, salary, start_date, department, manager |
| contract        | employee_name, position, salary, start_date, duration (or permanent) |
| onboarding      | employee_name, position, start_date, manager, first_day_location |
| policy_update   | policy_name, effective_date, summary_of_change |
| custom          | description of what the document should contain |

## Instructions
1. Ask user which document type they need.
2. Collect required details (prompt one by one if unsure).
3. Call Claude with:
   - Document type description
   - All provided details
   - Instruction: "Use [PLACEHOLDER] for missing fields"
   - Company name from env variable
4. Show 300-character preview.
5. Ask: [S]ave to output/ only / [D]rive too / [D]iscard
6. Save as: output/YYYY-MM-DD_[type]_[employee_name].md

## Output Filename Convention
```
output/2025-06-01_offer_letter_John_Smith.md
output/2025-06-01_onboarding_Jane_Doe.md
```

## Common Mistakes
- Not using placeholders for missing fields: always use [PLACEHOLDER].
- Saving without preview: always show preview first.
- Wrong filename: follow the convention above exactly.
