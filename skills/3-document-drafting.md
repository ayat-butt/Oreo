# Skill 3: Document Drafting

## Metadata
- **Trigger Phrases:** "draft contract", "create document", "generate offer letter", "onboarding email", "create agreement", "draft policy"
- **Input Files:** 8 files total (~1000 lines)
- **Output Location:** output/documents/contracts/[Employee Name]/
- **Dependencies:** Google Drive API connected, Claude API available
- **Execution Time:** ~10 minutes per document
- **Approval Required:** YES — Always preview before saving

## Input Files (Exact)
1. `skills/3-document-drafting.md` (this file)
2. `memory/MEMORY.md` (core context)
3. `memory/feedback_contract_*.md` (contract rules, ~5 files)
4. `draft_contract.py` (contract generation script)
5. `hr_assistant/contract_service.py` (contract service module)
6. `hr_assistant/drive_service.py` (Drive storage module)
7. `CLAUDE.md` (company guidelines)
8. Original email or user input (document request)

**Files NOT Loaded:**
- ❌ Email categorisation files
- ❌ Payroll files
- ❌ Calendar files
- ❌ Teams files
- ❌ Probation files

## Execution Flow
```
User: "Draft an offer letter for John Smith"
  ↓
Check: Google Drive API connected? (docs/setup-status.md)
Check: Claude API available? (ANTHROPIC_API_KEY in .env)
Check: Document type valid?
  ↓
Load: 8 input files + contract rules
  ↓
Execute:
  1. Ask user: Which document type? (offer_letter, contract, onboarding, policy, custom)
  2. Collect required details (one by one if unclear)
  3. Use draft_contract.py template for document type
  4. Call Claude to fill template with details
  5. Show 300-char preview to user
  6. Get approval: [S]ave to output / [D]rive too / [D]iscard
  7. Save to output/documents/contracts/[Employee Name]/
  8. Optional: Upload to Google Drive
  ↓
Output: output/documents/contracts/[Employee]/[TYPE]_[date]_[name].docx
  ↓
Verify: File created and accessible
Confirm: Show link to user
```

## Purpose
Generate HR documents (offer letters, contracts, onboarding packs, policy updates) using Claude AI and save them to output/ folder and optionally to Google Drive.

---

## ⭐ Contract Formatting Standards (LOCKED — apply to EVERY contract)

These are Ayat's confirmed formatting rules. **They are now auto-applied by `draft_contracts()` in [contract_service.py](../hr_assistant/contract_service.py)** — pass `is_transition=True` for internal transitions. Always review the generated doc against this list before sharing; keep formatting clean and consistent — no exceptions.

### 1. Header block (Date / CNIC / Name)
- **Bold the LABELS only** — `Date:`, `CNIC:`, `Name:`
- Do **NOT** bold the values next to them (the date, the CNIC number, the name).

  > **Date:** 10 June 2026   **CNIC:** 35201-6071382-2   **Name:** Momina Raja

### 2. First paragraph (the offer sentence)
- **Bold the name only** (salutation + name, e.g. **Ms. Momina Raja**) — do **NOT** bold the words in brackets (`(hereinafter referred to as …)`).
- Also bold: the **designation**, the **team/department**, and the **effective date**.
- **Always say only "Orenda"** in the first paragraph — never the full "Orenda Private Limited". Bold "Orenda".

### 3. Probation clause
- **Internal transitions** (existing employee moving teams/roles, e.g. Momina) → **REMOVE the probation clause entirely.**
- **All other (new) employees** → **KEEP the probation clause.**

### 4. HoD signing section
- **Always ASK who to list as the Head of Department / signatory** (name + designation) if it isn't already given in the details. Never assume.
- Signing date = today's date.

### 5. Offer Acceptance paragraph
- **Bold the employee's name AND CNIC number** here (e.g. **Momina Raja** … **35201-6071382-2**).

### 6. Page layout (page breaks)
- **Offer Acceptance** must start on a **new page.**
- **Job Description (Annexure-A)** must start on **another new page.**

### 7. Job Description (Annexure-A) formatting
- **Clean spacing — NO extra blank lines/spaces** between headings, sub-headings, or bullets.
- **Bold** the section heading (`Key Responsibilities`), the sub-headings (e.g. *Policy Research & Evidence Translation*), and keep bullets where required.
- Pull responsibilities verbatim from the JD doc (preserve dashes/characters exactly).
- ⚠️ Auto-extraction (`jd_doc_id`) only works when the JD doc uses a "Key Responsibilities" heading with proper sub-headings. If the JD is laid out differently (e.g. a "WHAT YOU'LL DO" section with plain-text sub-headings), insert the responsibilities manually following the clean format above.

### 8. Branded footer
- Single tree logo + **centered** address `2nd Floor, Time Square Plaza, Korang Road, I-10 Markaz, Islamabad | taleemabad.com`, 9pt grey, on every page. (Auto-applied by `_add_footer()`; never add a second logo — templates already embed one.)

### NDA
- NDA is well-written and well-formatted — use as-is.
- The `EMPLOYEEE` → `EMPLOYEE` heading typo has been fixed in both source templates (`nda_full_time`, `nda_project`) — no manual fix needed going forward.

## Document Types (LOCKED)

| Type | Required Details | Example |
|------|---|---|
| **offer_letter** | employee_name, position, salary, start_date, department, manager | Jane Doe, Senior Developer, $80k/year, 2026-06-01, Engineering, Ayat |
| **contract** | employee_name, position, salary, start_date, duration (or permanent) | John Smith, Manager, $100k/year, 2026-06-01, Permanent |
| **onboarding** | employee_name, position, start_date, manager, first_day_location | Muhammad, HR Specialist, 2026-06-01, Ayat, Office |
| **policy_update** | policy_name, effective_date, summary_of_change | Remote Work Policy, 2026-07-01, Allow hybrid 3 days/week |
| **custom** | description of what document should contain | [User specifies exactly what they need] |

## Mandatory Rules (LOCKED)

### Rule 1: Read Contract Rules Before Drafting
- Load ALL memory/feedback_contract_*.md files
- Understand: formatting standards, no edits allowed, verification requirements
- Check: Oreo signature rules, company guidelines
- These rules are non-negotiable

### Rule 2: Use Placeholders for Missing Fields
- If a required field is unknown: use [PLACEHOLDER]
- Example: If salary not confirmed: "Salary: [TO BE CONFIRMED]"
- Never guess or assume values
- User provides all data — wait for confirmation

### Rule 3: Templates Are Used As-Is
- Use draft_contract.py templates
- Only fill placeholders — never alter language or terms
- Templates are legally reviewed and approved
- Never customize wording without legal review

### Rule 4: Always Preview (300 characters minimum)
Before saving:
- Show user: document type, employee name, key details
- Show user: first 300 characters of generated content
- Format: display in readable way with formatting
- Get explicit approval: [S]ave only / [D]rive too / [D]iscard

### Rule 5: Save with Correct Filename Convention
**Format:** `output/documents/contracts/[Employee Name]/[YYYY-MM-DD]_[TYPE]_[EMPLOYEE].docx`

**Examples:**
```
output/documents/contracts/John_Smith/2026-05-12_contract_John_Smith.docx
output/documents/contracts/Jane_Doe/2026-05-12_offer_letter_Jane_Doe.docx
output/documents/contracts/Muhammad_Ahmed/2026-05-12_onboarding_Muhammad_Ahmed.md
```

### Rule 6: Collect Details Systematically
If any required field is missing:
- Ask user for it (one question at a time)
- Confirm before moving to next
- Never skip a required field
- Example:
  ```
  Document type: offer_letter
  Employee name: John Smith
  Position: [required] → "What is the position?"
  [Wait for answer]
  ```

### Rule 7: Contract Review Before Sending
- READ entire generated document
- Verify ALL fields filled correctly
- Check dates, amounts, formatting
- Read clauses for accuracy
- Only save after verification

### Rule 8: Google Drive Optional
- Ask user: "Save to Google Drive too?" [Y/N]
- If YES: upload file using drive_service.py
- Share with user (make sure they can access)
- Both local copy and Drive copy saved

## Claude Prompt Template (LOCKED)

```
Generate a [DOCUMENT_TYPE] for:
- Employee: [NAME]
- Position: [POSITION]
- Salary: [SALARY] (or [TO BE CONFIRMED])
- Start Date: [DATE]
- Department: [DEPARTMENT]
- Manager: [MANAGER]
[Additional fields as needed]

Use this template structure:
[Use draft_contract.py template content]

Requirements:
1. Fill ALL [PLACEHOLDER] fields with provided data
2. Use placeholders for unknown fields: [TO BE CONFIRMED]
3. Keep professional tone, formal language
4. Do NOT alter template text or terms
5. Company name: Taleemabad
6. Format: Professional document formatting

Return ONLY the document content (ready to save).
```

## Common Mistakes (LOCKED)

❌ **Mistake 1: Not Reading Contract Rules First**
- Always read memory/feedback_contract_*.md before drafting
- Understand formatting, signature rules, verification requirements
- Rules exist for legal/compliance reasons

❌ **Mistake 2: Altering Template Language**
- Templates are used as-is
- Only fill placeholders
- Never change terms, clauses, or wording
- If change needed: consult legal team first

❌ **Mistake 3: Guessing Missing Fields**
- Never assume employee details
- Use [PLACEHOLDER] if unsure
- Ask user for confirmation
- Wrong data = invalid contract

❌ **Mistake 4: Skipping Preview**
- Always show user 300+ characters of generated content
- Display in readable format with formatting
- Get explicit approval before saving
- Never auto-save

❌ **Mistake 5: Wrong Filename Convention**
- Follow format: output/documents/contracts/[Name]/[DATE]_[TYPE]_[NAME].docx
- Wrong names make files hard to find
- Organize by employee name (in folder)

❌ **Mistake 6: Not Reading Entire Generated Document**
- Read every clause and field
- Verify dates, names, amounts match requirements
- Check formatting is professional
- Spot errors before user sees them

❌ **Mistake 7: Saving Without User Approval**
- User must approve before saving
- Options: [S]ave to output / [D]rive too / [D]iscard
- Never assume approval
- Never auto-save

## Document Verification Checklist (LOCKED)

Before saving ANY document, verify:
- [ ] Employee name spelled correctly
- [ ] Position matches job title
- [ ] Salary amount is correct (if included)
- [ ] Start date is confirmed and correct
- [ ] Department is accurate
- [ ] Manager name is correct and spelled right
- [ ] All required fields are filled (no empty placeholders)
- [ ] Unknown fields use [TO BE CONFIRMED] format
- [ ] Document type is appropriate for use case
- [ ] Formatting is professional (no extra spaces, proper fonts)
- [ ] No template text left unfilled
- [ ] Company name is "Taleemabad"
- [ ] Signature line is included (if applicable)
- [ ] Date field reflects document creation date

## Output Format (LOCKED)

**File:** output/documents/contracts/[Employee_Name]/[YYYY-MM-DD]_[TYPE]_[NAME].[ext]

```
# Document Generated
**Date:** 2026-05-12  
**Type:** Offer Letter  
**Employee:** John Smith  
**Position:** Senior Developer  
**Salary:** $80,000/year  
**Start Date:** 2026-06-01  

---

## Document Content

Dear John,

We are pleased to extend an offer of employment for the position of Senior Developer 
at Taleemabad, effective 2026-06-01.

[Full document content...]

Your position reports to: Ayat Khan, Engineering Manager

We look forward to having you on our team.

Best regards,  
Taleemabad HR Team

---

## Metadata
- **User Approval:** YES
- **Saved Location:** output/documents/contracts/John_Smith/
- **Drive Upload:** [Y/N]
- **File Type:** .docx/.md
- **Ready to Send:** YES/NO

---

## Confirmation
✓ Document created
  Type: Offer Letter
  Employee: John Smith
  Preview: [First 300 chars]...
  Status: Ready to send to employee
```

## Instructions — Step by Step

1. **Identify Document Type**
   ```
   What document do you need?
   1. Offer Letter
   2. Contract
   3. Onboarding Email
   4. Policy Update
   5. Custom
   
   Choice: [1-5]
   ```

2. **Load Contract Rules**
   - Read memory/feedback_contract_*.md files
   - Understand formatting, signature rules
   - Check Oreo signature rules
   - Proceed with awareness of all requirements

3. **Collect Required Details**
   ```
   Document type: Offer Letter
   
   Employee name: [required] → "What is the employee's full name?"
   [Wait for answer: John Smith]
   
   Position: [required] → "What is their position?"
   [Wait for answer: Senior Developer]
   
   [Continue for all required fields...]
   ```

4. **Generate Document**
   - Use draft_contract.py template
   - Call Claude with prompt template
   - Include all provided details
   - Use [PLACEHOLDER] for unknowns

5. **Display Preview**
   ```
   Document Type: Offer Letter
   Employee: John Smith
   Position: Senior Developer
   
   Preview (first 300 chars):
   "Dear John, We are pleased to extend an offer of employment 
   for the position of Senior Developer at Taleemabad, effective 
   2026-06-01..."
   ```

6. **Get Approval**
   ```
   Save this document?
   [S]ave to output only
   [D]rive too (upload to Google Drive)
   [D]iscard (cancel)
   ```

7. **Save to Output**
   ```
   output/documents/contracts/John_Smith/
   2026-05-12_offer_letter_John_Smith.docx
   ```

8. **Upload to Drive (Optional)**
   ```
   Uploading to Google Drive...
   [File created with share link]
   ```

9. **Confirm to User**
   ```
   ✓ Offer letter created
   Employee: John Smith
   Position: Senior Developer
   Start Date: 2026-06-01
   
   Location: output/documents/contracts/John_Smith/
   Drive: [Share link if uploaded]
   
   Ready to send to employee
   ```

---

**Skill Status:** ✅ ACTIVE  
**Integration:** ✅ Google Drive + Claude API  
**Approval Required:** YES (always preview)  
**Template Edit:** ❌ NO (use as-is)  
**Drive Upload:** Optional (user choice)  
**Data Safety:** Local copy + Drive backup
