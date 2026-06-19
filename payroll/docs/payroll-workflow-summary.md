# PAYROLL WORKFLOW SUMMARY — Complete Reference

**Last Updated:** 2026-04-24  
**Status:** All 16 steps documented and locked in  
**Keyword:** PAYROLL (for isolation)

---

## Complete 16-Step Payroll Workflow

### Data Entry & Processing Steps (STEP 1-7, 11-14)

**STEP 1: Copy Previous Month's Payroll Sheet**
- Source: Zeeshan's Master Sheet (Payroll tab)
- Action: Copy PREVIOUS MONTH's REVISED payroll sheet
- Rename to: `PAYROLL SHEET - [CURRENT MONTH] [YEAR]`

**STEP 2: Addition/Deletion Process & Employee Count**
- Source: Addition/Deletion Tracker Sheet
- Sub-steps:
  - Remove resignees (from previous month deletion list)
  - Add new joiners (from current month addition list)
  - Calculate unpaid days for mid-month joiners: `(Gross ÷ 30) × Unpaid Days`
  - Calculate pending/arrears for late-month joiners: `(Gross ÷ 30) × Working Days`

**STEP 3: Add Commute/Travel Allowance**
- Who: CPD COACHES at NIETE ICT only
- Source: Commute/Travel Allowance Sheet (current month tab)
- Action: Copy exact amount from sheet for each coach

**STEP 4: Deduct Meal Charges**
- Who: NIETE ICT employees listed in sheet
- Source: Meal Deduction Sheet (current month tab)
- Amount: Fixed 5,720 per employee (no variation)

**STEP 5: Verify & Update Employee Salary Components**
- Check: Gross, Basic, Medical, Other Allowance
- Monitor: Email/Teams for salary change announcements
- Action: Update if changes communicated

**STEP 6: Add Approved Overtime Entries**
- Source: Markaz Overtime Management
- CRITICAL: DUAL APPROVAL REQUIRED:
  - Line Manager Status = APPROVED (green checkmark)
  - HR Status = "Moved to [CURRENT MONTH] PAYROLL"
- Action: Add overtime amount; manually cross-check calculation
- Formula: `(Gross ÷ 30 ÷ 8) × Hours = Overtime Amount`

**STEP 7: Add Pending Dues/Arrears**
- Source: User input (always ASK each month)
- Action: Add due amount for each employee with pending dues
- Common case: New joiners joining 24th-25th of previous month

**STEP 11: Add Advance Salary Deductions**
- Source: Advances Tracking Sheet (primary) + Markaz verification
- Action: Add exact PKR amount (full or partial)
- Cross-verify: Both Markaz and tracking sheet should match

**STEP 12: Add Loan Installments**
- Source: Loans tab (Advances & Loans sheet) + Markaz loan plans
- Action: Add THAT MONTH'S installment amount only
- Note: Recurring monthly deduction (unlike one-time advances)

**STEP 13: Add BusCaro Deduction**
- Source: BusCaro Tracking Sheet (current month tab)
- What: Commute service (60% company subsidy, 40% employee pays)
- Action: Add amount from "User" column for each route

**STEP 14: Add EOBI Deduction**
- Amount: Fixed PKR 370 per month
- Who: All regular employees
- Exception: Interns (user will specify)
- Action: Copy from previous month + add new joiners (except interns)

---

### Calculation Steps (STEP 8, 9, 15, 16)

**STEP 8: Calculate Total Allowance**
```
Total Allowance = Gross + Basic + Medical + Other + Overtime + Commute + Pending
```
- 7 components from previous steps
- Calculate fresh for each employee (don't copy previous month)
- Reason: Overtime, commute, pending change monthly

**STEP 9: Calculate Taxable Salary**
```
Taxable Salary = Total Allowance - Unpaid Days - Medical Allowance
```
- Used for income tax calculation
- Medical allowance is tax-exempt

**STEP 10: Add Income Tax (IT) Deduction**
- **LOOKUP-BASED** (NOT calculation-based)
- Source: TAX DEDUCTION DETAILS Sheet
- Process: Find employee → Find current month column → Get amount
- Handle negatives: Tax credits shown in parentheses (enter as -value)
- Handle blanks: Blank = 0 IT for that month

**STEP 15: Calculate Total Deductions**
```
Total Deductions = IT + Unpaid Days + Abhi + Advance + Loan + BusCaro + Lunch + EOBI
```
- 8 components from all previous steps
- Add all (use 0 if component not applicable)
- Calculate fresh for each employee

**STEP 16: Calculate Net Salary (Take-Home Pay)**
```
Net Salary = Total Allowance - Total Deductions
```
- Final employee salary after all deductions
- Enter in "Net Salary [Month]" column

---

### Verification Steps

**Variance Analysis:**
```
Variance = Current Month Net - Previous Month Net
```
- Document reasoning for ALL non-zero variances
- Common reasons:
  - Overtime added/removed
  - Advance taken
  - New joiner (unpaid days)
  - Employee leaving (unpaid days)
  - Salary changes
  - Loan added/changed
  - BusCaro deduction added

---

## Critical Reference Data

### Data Sources & Links

| Source | Link | Used in |
|--------|------|---------|
| Zeeshan's Master Sheet | https://docs.google.com/spreadsheets/d/1BAVwEkHqVSzrqV-yafH7I0mWp9AI4Z2Om24Plydj49Q/edit | STEP 1 |
| Addition/Deletion Tracker | https://docs.google.com/spreadsheets/d/18x6R4Gl3P_D-Dn_HHtLpXbpwQnqVafO6rekvovcVICk/edit | STEP 2 |
| Commute Allowance | https://docs.google.com/spreadsheets/d/10kM4xcC0S7nSJhU5HfH6ZdbiTxqyzw5P4_z5nOJ7lck/edit | STEP 3 |
| Meal Deduction | https://docs.google.com/spreadsheets/d/1iZMCJe6aHxxwVsCKpIqzu4g4ZAvYci76noOeSB2byD4/edit | STEP 4 |
| Markaz Overtime | https://markaz.taleemabad.com/overtime-loans-advances | STEP 6 |
| TAX DEDUCTION DETAILS | https://docs.google.com/spreadsheets/d/1nw09utC0x3WFsTEM2Qj548y289FUoccPTW3jft3LeFs/edit | STEP 10 |
| Advances Tracking | https://docs.google.com/spreadsheets/d/1sxXfGghw1cGuTsP15VZMxXCxkT1SxY61UNmHMp6vtBE/edit | STEP 11 |
| Loans Tab | (Same as Advances) | STEP 12 |
| BusCaro Tracking | https://docs.google.com/spreadsheets/d/12EyDg8UAuDFexpJ_oC7hCN2HU0lDuQbAHHkmbdFKJwQ/edit | STEP 13 |
| Markaz Loans | https://markaz.taleemabad.com/overtime-loans-advances | STEP 12 |

### Pakistan Income Tax Slabs (2025-2026) — Reference Only

| Slab | Range | Fixed Tax | Rate |
|------|-------|-----------|------|
| BTL | Below 600,000 | — | 0% |
| 1 | 600,001-1,200,000 | — | 1% |
| 2 | 1,200,001-2,200,000 | 6,000 | 11% |
| 3 | 2,200,001-3,200,000 | 116,000 | 23% |
| 4 | 3,200,001-4,100,000 | 346,000 | 30% |
| 5 | 4,100,001+ | 616,000 | 35% |

*Note: Finance team pre-calculates IT. You lookup the amount only.*

### Fixed Amounts (No Variation)

- **Meal Deduction:** PKR 5,720 (NIETE ICT only, STEP 4)
- **EOBI:** PKR 370 (all employees except interns, STEP 14)
- **Days per Month:** 30 (standard, used for all per-day calculations)

### Entities

- OPL
- OWL
- NIETE ICT
- NIETE BALOCHISTAN
- TALEEMABAD INC

---

## Quality Assurance Checklist

Before finalizing payroll:

**Employee Verification (4-Step — MANDATORY):**
- [ ] Match FULL NAME (exact spelling)
- [ ] Match EMPLOYEE ID
- [ ] Match ENTITY
- [ ] Match OTHER DETAILS (salary, designation, etc.)

**Data Entry Verification:**
- [ ] All STEP 1-7 data entered correctly
- [ ] All deductions added (IT, advances, loans, BusCaro, lunch, EOBI)
- [ ] All calculations are mathematically correct
- [ ] No values doubled or skipped
- [ ] All deductions are reasonable for employee level
- [ ] Variance analysis documented for all changes

**Reference Verification:**
- [ ] Previous month's payroll reviewed
- [ ] Current month's reference sheets checked
- [ ] All new joiners added with unpaid days calculated
- [ ] All resignees removed
- [ ] Email/Teams monitored for salary changes

---

## Common Issues & Solutions

**Issue:** Employee net salary is negative
- **Cause:** Total deductions > Total allowance
- **Action:** Review all deductions; flag for finance team review

**Issue:** Variance is unexpectedly large
- **Cause:** Missing reason documentation
- **Action:** Check all deductions and allowances; document reason

**Issue:** Employee not found in reference sheet
- **Cause:** Possible name spelling mismatch or employee off payroll
- **Action:** Verify employee name; cross-check addition/deletion tracker

**Issue:** Advance/Loan amount differs between sources
- **Cause:** Inconsistent data
- **Action:** Cross-verify both Markaz and tracking sheet; ask user which is correct

---

## Processing Timeline

- **Start Date:** 17th of each month
- **Payroll Month:** Current month (17th-30th of current month covers NEXT month's payroll)
- **Financial Year:** July-June (not calendar year)

---

## Contact & Escalation

If any step requires clarification or data is unavailable:
- **STEP 7 (Pending Dues):** Ask user explicitly each month
- **STEP 12 (Loans):** Verify with Markaz or finance team
- **STEP 13 (BusCaro):** Verify with transport/admin team
- **Abhi (STEP 15 component):** [TBD - awaiting clarification]
- **Interns (STEP 14):** User will specify

---

**Status:** Complete & Ready for Monthly Processing  
**Last Updated:** 2026-04-24 | Session 3 Complete
