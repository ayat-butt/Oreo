# Skill 7: Payroll Processing

## Metadata
- **Trigger Phrases:** "payroll", "salary processing", "process payroll", "April payroll", "employee payment", "tax deduction", "pending dues", "overtime approval"
- **Input Files:** Isolated payroll/ folder (~1000+ lines)
- **Output Location:** payroll/output/ (COMPLETELY ISOLATED)
- **Dependencies:** Google Sheets API, Email/Teams for salary changes, Markaz DB (read-only)
- **Execution:** Monthly (variable date based on business cycle)
- **Approval Required:** YES — Multiple verification layers (7-step mandatory protocol)

## ⚠️ CRITICAL: COMPLETE ISOLATION

**When user says "PAYROLL" (any form):**
1. **Switch context immediately** → payroll/ folder ONLY
2. **Load:** payroll/CLAUDE.md (overrides root CLAUDE.md)
3. **Use:** payroll/SESSIONS.md, payroll/memory.md
4. **Write:** payroll/output/ ONLY
5. **Never mix** with contracts/onboarding/HR tasks
6. **Never reference** root context, skills, or non-payroll work

**Why:** One wrong entry = affects someone's actual salary. Zero tolerance.

## Input Files (EXACT)
1. `payroll/CLAUDE.md` (payroll context & rules)
2. `payroll/memory.md` (34KB of critical protocols)
3. `payroll/SESSIONS.md` (progress tracking)
4. Google Sheet: Payroll Data (provided by user)
5. Email/Teams: Salary change notifications
6. `memory/feedback_payroll_*.md` (all 7 mandatory rules)
7. Markaz DB: Read-only employee verification

**Files NOT Loaded:**
- ❌ Email categorisation files
- ❌ Contract files
- ❌ Probation files
- ❌ Calendar files
- ❌ Teams files (unless salary changes in Teams)

## Execution Flow (7-Step Mandatory Protocol)
```
User: "Process April payroll"
  ↓
[STEP 0] CONTEXT ISOLATION
  Switch to payroll/ folder
  Load payroll/CLAUDE.md
  Load payroll/memory.md (read ALL mandatory rules)
  ↓
[STEP 1] EMPLOYEE VERIFICATION (4-Sub-steps per employee)
  For EVERY employee:
    1a. Match full name EXACTLY (typos cause wrong salary)
    1b. Verify employee ID matches
    1c. Confirm entity/company is correct
    1d. Cross-check other details against Markaz
  If ANY mismatch: STOP, ask user to verify
  ↓
[STEP 2] GATHER ALL DATA
  Collect from user:
    - Salary data (Google Sheet or manual input)
    - Salary changes (promotions, increments, transitions)
    - Pending dues (new joiners, retroactive payments)
    - Overtime approvals (with manager + HR sign-off)
    - Tax deductions (if applicable)
    - Attendance/leaves data
  ↓
[STEP 3] APPLY MANDATORY FORMULAS (EXACT ORDER)
  For each employee, calculate IN THIS ORDER (no variations):
    1. Basic = Gross × 90%
    2. Medical = Basic × 10%
    3. Other = Gross - Basic - Medical
    4. Total Allowance = sum of all allowances
    5. Taxable = Total Allowance - Medical - Unpaid Days
    6. Deductions = sum of 8 items
    7. Net = Allowances - Deductions
  ↓
[STEP 4] CROSS-CHECK CALCULATIONS
  Verify BEFORE saving:
    - Basic + Medical + Other = Gross (within rounding)
    - All deductions itemized (8 items: tax, social, insurance, etc.)
    - Net = Gross - Deductions (basic math check)
    - Compare vs. previous month (flag if changed > 10%)
  ↓
[STEP 5] MONITOR & APPLY SALARY CHANGES
  Watch for changes in:
    - Promotions (new salary, retroactive)
    - Increments (date effective, amount)
    - Part-time transitions (prorated salary)
    - Status changes (active, suspended, terminated)
  Extract from: emails, Teams messages, user input
  Apply ONLY after 4-step verification
  ↓
[STEP 6] DUAL-APPROVAL PROTOCOL (Overtime Only)
  If overtime present:
    Manager Status MUST = "APPROVED"
    HR Status MUST = "Moved to [MONTH] PAYROLL"
    Manual calculation cross-check: verify hours × rate
  ↓
[STEP 7] GENERATE & VALIDATE PAYROLL REPORT
  Create payroll/output/[month]_payroll_final.csv
  Include: Name, ID, Gross, Basic, Medical, Allowances, Deductions, Net
  Validate: Row count = employee count, all formulas match
  Final review by user BEFORE applying to system
  ↓
Output: payroll/output/[YYYY-MM]_payroll_final.csv
  ↓
Confirm: Show summary to user with all calculations
Log: payroll/SESSIONS.md updated with completion
```

## Purpose
Process monthly payroll with absolute accuracy:
1. Verify every employee (name, ID, entity)
2. Calculate allowances & deductions using exact formulas
3. Apply salary changes from emails/Teams
4. Handle overtime with dual approval
5. Generate validated payroll CSV for system import

## Mandatory Rules (LOCKED — ZERO EXCEPTIONS)

### Rule 1: Formulas (EXACT Order, No Variations)
```
Basic Salary         = Gross × 90%
Medical Allowance    = Basic × 10%
Other Allowance      = Gross - Basic - Medical
Total Allowance      = sum of all allowances
Taxable Income       = Total Allowance - Medical - Unpaid Days
Total Deductions     = sum of 8 items
Net Salary           = Total Allowance - Total Deductions
```

**Why:** Used for salary calculations across all employees — must be consistent.  
**How to apply:** Every employee, every month, in this exact order. No shortcuts.

### Rule 2: Employee Verification (4-Step, EVERY Entry)
Before entering ANY salary data:
1. **Full Name Match** — Spell correctly, compare against Markaz
2. **Employee ID** — Verify against official records
3. **Entity/Company** — Confirm Taleemabad vs. subsidiary
4. **Other Details** — Department, designation, status

**Why:** One wrong entry = wrong person gets wrong salary = catastrophic.  
**How to apply:** Verify BEFORE entering data. If unsure, ask user. Stop processing until confirmed.

### Rule 3: Salary Change Alerts (MONITOR VIGILANTLY)
Monitor emails & Teams for:
- **Promotions** — New salary, retroactive date
- **Increments** — Annual/special increases, effective date
- **Part-time Transitions** — Prorated salary calculation
- **Status Changes** — Active/suspended/terminated, effective date

**Why:** Salary changes are common. Missing one = employee gets wrong salary.  
**How to apply:** Check emails & Teams daily during payroll month. Extract dates carefully. Apply in STEP 5 ONLY after 4-step verification.

### Rule 4: Pending Dues Protocol (ASK EVERY MONTH)
At start of EVERY payroll processing:
```
❓ "Are there pending dues for this month?"
   (Manually tracked by HR, not in systems)
```

Common cases:
- New joiners on 25th (partial month, retroactive)
- Retroactive payments from previous months
- Bonuses or special adjustments

**Why:** Pending dues aren't in the system — HR tracks manually. Missing = unfair.  
**How to apply:** Always ask. Listen carefully. Verify amounts. Add to payroll if applicable.

### Rule 5: Overtime Approval (Dual-Approval Required)
If overtime hours present:
- **Manager Status** MUST = "APPROVED"
- **HR Status** MUST = "Moved to [MONTH] PAYROLL"
- **Manual Calculation** — Cross-check: (Hours × Rate) before adding to payroll

**Why:** Overtime is expensive. Dual approval prevents fraud/errors.  
**How to apply:** Check both statuses. If either missing, halt payroll for that employee. Calculate manually to verify.

### Rule 6: Deduction Categories (8 Items)
These 8 items make up "Total Deductions":
1. Income Tax
2. Social Security/Mandatory Contributions
3. Health Insurance Premium
4. Professional Membership Dues
5. Loan Installments
6. Provident Fund Contribution
7. Utility Bills/Advances (if applicable)
8. Other Deductions (specify)

**Why:** Consistent deduction categories across all employees.  
**How to apply:** Itemize all 8 for each employee. Sum to "Total Deductions" in formula.

### Rule 7: Cross-Check Validation (BEFORE Saving)
ALWAYS verify:
- Basic + Medical + Other = Gross (within ±0.50 rounding)
- All 8 deductions itemized
- Net = Gross - Total Deductions (math check)
- Compare vs. previous month (flag if > 10% change)
- Row count in CSV = number of employees

**Why:** Catches errors before they go live.  
**How to apply:** Use spreadsheet formulas to auto-verify. Show user summary. Get approval.

## Common Mistakes (LOCKED)

❌ **Mistake 1: Skipping Employee Verification**
- Don't assume you know the employee
- Match name exactly, verify ID, check entity
- One wrong entry = wrong person's salary
- Always verify, always confirm

❌ **Mistake 2: Wrong Formula Order**
- Formulas MUST be applied in exact order (1→2→3→4→5→6→7)
- Don't calculate Net directly — use intermediate steps
- Net must = Gross - Deductions (verify at end)

❌ **Mistake 3: Missing Salary Changes**
- Monitor emails & Teams vigilantly
- Extract promotions, increments, transitions
- Apply changes in STEP 5 ONLY (after 4-step verification)
- Never miss a change — results in wrong salary

❌ **Mistake 4: Forgetting Pending Dues**
- Always ask: "Are there pending dues?" at start
- Never assume "none"
- Pending dues are manually tracked, not in systems
- Ask, verify, add

❌ **Mistake 5: Overtime Without Dual Approval**
- Manager Status must = "APPROVED"
- HR Status must = "Moved to [MONTH] PAYROLL"
- Calculate manually (Hours × Rate) to verify
- Don't add overtime if either approval missing

❌ **Mistake 6: Not Validating Before Saving**
- Cross-check all calculations before output
- Use spreadsheet formulas to verify
- Flag > 10% changes for user review
- Never save unvalidated payroll

❌ **Mistake 7: Mixing Non-Payroll Context**
- Isolation is CRITICAL
- Don't reference contracts, onboarding, probation
- Only load payroll/ folder
- NEVER break isolation

## Session Structure (Per Payroll Month)

Each payroll session follows this:

| Step | Task | Owner | Output |
|------|------|-------|--------|
| 1 | Load payroll/memory.md (read all rules) | Oreo | Rule review |
| 2 | Gather data (sheet, changes, dues) | User+Oreo | Data file |
| 3 | Verify employees (4-step per person) | Oreo | Verification log |
| 4 | Calculate (formulas, allowances, deductions) | Oreo | Calculation sheet |
| 5 | Apply salary changes (monitor emails/Teams) | Oreo | Change log |
| 6 | Overtime approval verification | Oreo | Approval checklist |
| 7 | Validate & finalize (cross-checks) | Oreo | Validation report |
| Final | User review & approval | User | Final sign-off |
| Archive | Save to payroll/output/ | Oreo | payroll/output/[month]_payroll_final.csv |

Session tracked in: payroll/SESSIONS.md

## Output Format

**File:** payroll/output/[YYYY-MM]_payroll_final.csv

| Employee | ID | Entity | Gross | Basic | Medical | Other | Total Allow | Taxable | Tax | Deduct1 | Deduct2 | ... | Deduct8 | Total Deduct | Net |
|----------|----|----|-------|-------|---------|-------|-------------|---------|-----|---------|---------|-----|---------|--------------|-----|
| John Smith | 001 | Taleemabad | 50000 | 45000 | 4500 | 500 | 49000 | 48500 | 5200 | ... | 8000 | 41000 |
| Jane Doe | 002 | Taleemabad | 60000 | 54000 | 5400 | 600 | 58800 | 58200 | 6200 | ... | 9500 | 49300 |

## Markaz Integration (Read-Only)

Markaz DB is used for:
- Employee name verification (cross-check)
- Employee ID verification (match records)
- Entity/company verification
- Department & designation verification

**RULE:** Never write, modify, or delete in Markaz. Read-only access only.

Script: Uses MARKAZ_DB_URL from .env (PostgreSQL connection)

## Memory & Protocols

All detailed payroll rules live in:
- `payroll/memory.md` (34KB of accumulated knowledge)
- `memory/feedback_payroll_*.md` (7 mandatory rule files)

At start of EVERY payroll session, read:
```
1. payroll/memory.md
2. memory/feedback_payroll_formulas_critical.md
3. memory/feedback_payroll_employee_verification.md
4. memory/feedback_payroll_salary_change_alerts.md
5. memory/feedback_payroll_overtime_approval_protocol.md
6. memory/feedback_payroll_pending_dues_protocol.md
7. memory/feedback_payroll_always_separate.md
```

---

**Skill Status:** ✅ ACTIVE (ISOLATED)  
**Isolation:** ✅ COMPLETE  
**Mandatory Protocols:** 7 (all locked)  
**Approval Required:** Multi-layer (7 steps)  
**Data Safety:** Critical — git-backed, reversible  
**Risk Level:** CRITICAL (wrong entry = wrong salary)  
**Zero Tolerance:** YES — absolute accuracy required
