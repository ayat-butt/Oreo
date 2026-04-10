# Skill: Document Drafting

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
