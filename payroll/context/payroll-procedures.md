# Payroll Procedures & Policies

Company payroll procedures, policies, and standards for Taleemabad office.

## 📌 Important Note on Reference Sheets

Many payroll reference sheets contain multiple months of data, but **only the CURRENT MONTH is visible** (other months are hidden). This is intentional design for clarity and focus:
- Data preserved: All months' history stored in the sheet
- Visibility: Only current month shown to reduce clutter
- Example: Meal deduction sheet shows April's employees clearly, but Feb/March data is hidden
- When working on a new month: That month's data becomes visible as other months are hidden

---

## ⚠️ CRITICAL: Employee Verification Protocol

**MANDATORY before EVERY payroll entry.** One wrong entry affects an employee's salary - ZERO tolerance for errors.

### 4-Step Verification (Non-negotiable)
1. **Match FULL NAME** — Exact spelling match, don't assume abbreviations
2. **Match EMPLOYEE ID** — IDs must match exactly
3. **Match ENTITY** — Correct entity section (OPL, OWL, NIETE ICT, etc.)
4. **Match OTHER DETAILS** — Salary, designation, or other identifying info

### Verification Sources
- Payroll sheet itself
- Addition/Deletion Tracker
- Gmail/Contracts
- Reference sheets (meal deduction, commute allowance)

### Stop and Verify If:
- Name spelling differs
- Employee ID doesn't match
- Entity doesn't match
- Employee not found in payroll
- Multiple employees with similar names
- ANY uncertainty about details

**See:** feedback_payroll_employee_verification.md for complete protocol

## Monthly Payroll Cycle

**Start Date:** 17th of each month

### STEP 1: Copy Previous Month's Payroll Sheet ✅
**Where:** Zeeshan's Master Sheet (Payroll tab)
**Link:** https://docs.google.com/spreadsheets/d/1BAVwEkHqVSzrqV-yafH7I0mWp9AI4Z2Om24Plydj49Q/edit?gid=0#gid=0

**Process:**
1. Open Zeeshan's Master Sheet
2. Go to "Payroll" tab
3. Find the PREVIOUS month's REVISED payroll sheet
4. Create a copy of that sheet
5. Rename as: `PAYROLL SHEET - [CURRENT MONTH] [YEAR]`

**Example:**
- Current: March 2026
- Copy from: February 2026 (REVISED VERSION)
- Rename to: PAYROLL SHEET - MARCH 2026

### STEP 2: Addition/Deletion Process & Employee Count Adjustment ✅

**Reference Sheet:** Addition/Deletion Tracker Sheet
**Link:** https://docs.google.com/spreadsheets/d/18x6R4Gl3P_D-Dn_HHtLpXbpwQnqVafO6rekvovcVICk/edit?gid=1365091393#gid=1365091393

**Also check:** Gmail/Contracts for new joiner verification

**Sub-step 2A: Remove Resignees**
- Go to Addition/Deletion Tracker → Previous Month's Tab (e.g., February)
- Find "Deletion" section
- Remove all listed employees from current payroll (March)
- Ensure they don't appear in active employee list

**Sub-step 2B: Add New Joiners**
- Go to Addition/Deletion Tracker → Current Month's Tab (e.g., March)
- Find "Addition" section
- Extract: Name, joining date, entity, gross salary
- Verify salary via Gmail/contracts if needed
- Add to payroll in correct entity section

**Sub-step 2C: Calculate Unpaid Days (Mid-Month Changes)**

**What are Unpaid Days:**
- Days when employee was NOT working/present in the month
- Days not paid (salary deduction for that period)
- First month only for joiners; final month for leavers

**Unpaid Days Formula:**
```
Unpaid Days Amount = (Gross Salary ÷ 30) × Number of Unpaid Days
```

**Scenario 1: Employee Joins Mid-Month (5th onwards)**

Days 1-4 are unpaid (didn't work yet)

**Example:** Employee joins 10th April with 105,000 gross
- Unpaid days: 9 (1st-9th April)
- Per day amount: 105,000 ÷ 30 = 3,500
- Unpaid amount: 3,500 × 9 = 31,500
- Action: Add 31,500 to "Unpaid Days" column in April payroll

**Another Example:** Employee joins 5th March with 105,000 gross
- Unpaid days: 4 (1st-4th March)
- Per day amount: 105,000 ÷ 30 = 3,500
- Unpaid amount: 3,500 × 4 = 14,000
- Action: Add 14,000 to "Unpaid Days" column in March payroll

**Scenario 2: Employee Leaves Mid-Month (Before 30th)**

Days after last working day are unpaid (no longer working)

**Example:** Employee's last working day is 23rd April with 110,000 gross
- Unpaid days: 7 (24th-30th April)
- Per day amount: 110,000 ÷ 30 = 3,667
- Unpaid amount: 3,667 × 7 = 25,669
- Action: Add 25,669 to "Unpaid Days" column in April payroll

**Data Source:** Addition/Deletion Tracker sheet
- Joining date → Calculate unpaid days for joining month
- Last working date → Calculate unpaid days for final month

**Sub-step 2D: Calculate Pending/Arrears (Joining 24th-25th of previous month)**
**Formula:** (Gross Salary ÷ 30) × Working Days

**Example:** Employee joins 25th February with 110,000 gross
- Didn't pay in Feb (too late in payroll cycle)
- Working days in Feb: 6 (25th-29th Feb, or 25th-28th depending on days in month)
- Per day amount: 110,000 ÷ 30 = 3,667
- Pending amount: 3,667 × 6 = 22,000
- Action: Add 22,000 to "Pending Amount/Arrears" in March payroll

**Sub-step 2E: Maintain Entity Organization**
**Entities:** OPL, OWL, NIETE ICT, NIETE BALOCHISTAN, TALEEMABAD INC
- Place new employees in correct entity section
- Match entity from Addition/Deletion tracker
- Maintain consistent organization structure

### STEP 3: Add Commute/Travel Allowance (NIETE ICT CPD COACHES) ✅

**Reference Sheet:** Commute/Travel Allowance Sheet
**Link:** https://docs.google.com/spreadsheets/d/10kM4xcC0S7nSJhU5HfH6ZdbiTxqyzw5P4_z5nOJ7lck/edit?gid=1513167551#gid=1513167551

**Who receives:** CPD COACHES at NIETE ICT entity ONLY

**Purpose:** Travel allowance given in advance each month for official school visits/commute

**Updates:** Monthly changes - employees added, removed, amounts changed

**Process:**
1. Open Commute/Travel Allowance Sheet
2. Navigate to current month's tab (e.g., March 2026)
3. Identify all CPD COACH names
4. Read commute allowance amount next to each name
5. Add exact amount to payroll → "Commute Allowance" column
6. Only for employees listed in that month's sheet

**CRITICAL NOTES:**
- ⚠️ No room for mistakes in payroll
- Must match exact amounts from source sheet
- Only NIETE ICT employees (CPD COACHES)
- Sheet updated monthly with additions/removals/changes
- Verify each entry carefully

**Example:**
- Sheet shows: Coach Ali = 2,000 commute allowance for March
- Add: 2,000 to Coach Ali's March payroll under Commute Allowance

### STEP 4: Deduct Meal Charges (NIETE ICT EMPLOYEES) ✅

**Reference Sheet:** Meal Deduction Sheet
**Link:** https://docs.google.com/spreadsheets/d/1iZMCJe6aHxxwVsCKpIqzu4g4ZAvYci76noOeSB2byD4/edit?gid=947033228#gid=947033228

**Who deducted from:** NIETE ICT employees who avail lunch/meal services

**Deduction Amount:** 5,720 per month (fixed)

**Updates:** Monthly - based on employee enrollment in meal services

**Process:**
1. Open Meal Deduction Sheet
2. Go to current month's tab (e.g., March 2026)
3. Read all employee names listed
4. For each listed employee, deduct 5,720
5. Add to payroll → "Meal Deductions" column
6. Only deduct for employees explicitly listed in the sheet

**CRITICAL NOTES:**
- Fixed deduction: 5,720 per month
- Only NIETE ICT entity employees
- Only those listed in current month's sheet
- If not listed, no deduction

**Example:**
- Sheet lists: Employee A, Employee B, Employee C for March
- Deduct: 5,720 from each of these 3 employees
- Others not listed: No meal deduction

### STEP 5: Verify & Update Employee Salary Components ✅

**Purpose:** Confirm all salary entries are correct; update any changed salaries

**Salary Components to Verify (ALL employees):**
- Gross Salary
- Basic Salary
- Medical Allowance
- Other Allowance
- Any other salary structure components

**Verification Process:**
1. Check payroll sheet (copied from previous month)
2. Verify each employee's entries are correct
3. Errors should be minimal (from copy process)
4. But VERIFY all entries are accurate

**Possible Salary Changes:**
Employees' salaries may change due to:
- Part-time model transitions
- Salary increments/updates/promotions
- Structural changes
- Other reasons

**How Changes Are Communicated:**
1. **Direct notification** — Ayat tells you about specific changes
2. **Email** — Salary change announcements via email
3. **Microsoft Teams** — Notifications in Teams groups

**Actions When Changes Occur:**
1. Extract salary change information carefully
2. Identify affected employee
3. Verify 4-step employee verification (name, ID, entity, details)
4. Update Gross Salary, Basic Salary, and other affected components
5. Document which employees had updates

**CRITICAL ALERT:**
- ⚠️ BE VIGILANT for email and Teams communications
- ⚠️ Monitor for salary change announcements
- ⚠️ Don't assume no changes - check for notifications
- ⚠️ Email and Teams are official channels

**Example:**
- Email received: "Muhammad Ali (ID 205) promoted - new gross salary 125,000"
- Action: Find Muhammad Ali in payroll, verify ID 205 and entity
- Update: Change gross salary to 125,000
- Document: Note the change in this step

### STEP 6: Add Approved Overtime Entries ✅

**Reference:** Taleemabad Markaz Overtime Management
**Link:** https://markaz.taleemabad.com/overtime-management

**Purpose:** Add overtime amounts for employees who have:
1. ✅ APPROVED line manager status
2. ✅ HR status showing "Moved to [CURRENT MONTH] PAYROLL"

**Overtime Calculation:**
```
Per Day Salary = Gross Salary ÷ 30 days
Per Hour Rate = Per Day Salary ÷ 8 hours
Overtime Amount = Per Hour Rate × Overtime Hours Worked
```

**MANDATORY DUAL APPROVAL (Both required):**

✅ **Approval 1: Line Manager Status = APPROVED**
- Must show green checkmark
- NOT Pending status
- Line manager has explicitly approved

✅ **Approval 2: HR Status = "Moved to [CURRENT MONTH] PAYROLL"**
- Examples: "Moved to April 2026 Payroll"
- Examples: "Moved to March 2026 Payroll"
- HR department moved request to this month

**❌ DO NOT ADD if:**
- Status = PENDING (not manager approved)
- HR Status = "NO STATUS" or blank
- HR Status shows different month (past or future)
- Either approval condition missing

**Data Verification Steps:**
1. Verify employee identity (4-step verification: name, ID, entity, details)
2. Manually recalculate overtime amount using formula
3. Cross-check gross salary from Markaz vs. payroll sheet
4. Verify overtime hours are accurate
5. Double-check per hour rate calculation

**EXAMPLE 1 - DO NOT ADD:**
- Employee: Fatima Rehman
- Line Manager Status: 🟡 PENDING (not approved)
- HR Status: NO STATUS (not updated)
- Action: SKIP until both approvals are received

**EXAMPLE 2 - ADD:**
- Employee: Abdurrehman Afridi
- Line Manager Status: ✅ APPROVED (green checkmark)
- HR Status: "Moved to August 2025 Payroll" ✅
- Hours: 8 hours
- Overtime Amount: PKR 7,208
- Action: ADD to payroll

**Process:**
1. Open Taleemabad Markaz Overtime Management
2. Look for requests with current month in HR Status
3. Check BOTH approval conditions are met
4. Verify employee identity completely (4-step)
5. Manually cross-check overtime calculation
6. Add overtime amount to payroll → "Overtime" column
7. Document which employees received overtime pay

**⚠️ CRITICAL ALERTS:**
- Very tricky step - requires extreme vigilance
- Always manually verify calculations
- Gross salary MUST match between Markaz and payroll
- Never add pending or unapproved requests
- HR status MUST show correct payroll month
- One wrong entry affects employee salary

### STEP 7: Add Pending Dues/Arrears ✅

**Purpose:** Include any pending dues or arrears owed to employees in current month payroll

**What are Pending Dues:**
- Salary or benefits owed from previous periods
- Dues carried forward from past months
- Additional payments that must be given to employee
- Amounts owed but not yet paid

**Common Scenario: New Joiner on 25th of Previous Month**

When employee joins late in month (24th-25th onwards):
- Too late to pay in that month (payroll closes 24th-25th)
- Payment deferred to next month
- Calculated and added as "pending dues" in next month's payroll

**Calculation:**
```
Per Day Salary = Gross Salary ÷ 30
Pending Due = Per Day Salary × Days Worked
```

**Example:**
- Employee joined: 25th February 2026
- Days worked in Feb: 6 days (25, 26, 27, 28, 29, Mar 1... wait, Feb has 28 days)
- Actually days worked: 5 days (25-29 Feb)
- Gross Salary: 110,000
- Per Day: 110,000 ÷ 30 = 3,667
- Pending Due: 3,667 × 5 = 18,335
- Added to: March 2026 payroll as pending due

**Other Pending Dues Cases:**
- Salary corrections from previous months
- Unpaid allowances or benefits
- One-time payments owed
- Custom cases specific to employee history
- Any company-specific pending amounts

**How to Get Pending Dues Information:**

✅ **ALWAYS ASK USER:**
- "Are there any pending dues for this month's payroll?"
- "Which employees have arrears or dues to be added?"
- "Are there any salary corrections or one-time payments?"

**Why ask every time:**
- Not stored in sheets or systems
- Only user knows about custom cases
- Tracked manually by HR
- Changes month to month
- Do NOT assume previous month's dues continue

**Data Verification:**
1. Get employee name and due amount from user
2. Verify employee identity (4-step verification: name, ID, entity, details)
3. Confirm reason for pending due
4. Verify amount is correct
5. Add to payroll → "Pending Dues" or "Arrears" column

**Process for Each Pending Due:**
1. ✅ Ask user for list of employees with pending dues
2. ✅ Get: Employee name, amount, reason
3. ✅ Verify: 4-step employee verification
4. ✅ Add: Amount to "Pending Dues" column
5. ✅ Document: Which employees received dues and amounts

**⚠️ CRITICAL NOTES:**
- DO NOT assume dues from previous month apply to current month
- Always ask explicitly - don't skip this step
- Manual tracking only - not in automated systems
- User is sole source for pending dues information
- Verify each entry carefully before adding

### STEP 8: Calculate Total Allowance ✅

**Purpose:** Calculate total allowance for each employee by summing all allowance components

**Total Allowance Formula:**
```
Total Allowance = Gross Salary + Basic Salary + Medical Allowance + Other Allowance + Overtime + Commute Allowance + Pending Dues
```

**Seven Components to Add (for EACH employee):**

| Component | Source | Notes |
|-----------|--------|-------|
| Gross Salary | STEP 1 (copied) or STEP 5 (if changed) | Stable unless salary changed |
| Basic Salary | STEP 1 (copied) or STEP 5 (if changed) | Stable unless salary changed |
| Medical Allowance | STEP 1 (copied) or STEP 5 (if changed) | Stable unless salary changed |
| Other Allowance | STEP 1 (copied) or STEP 5 (if changed) | Stable unless salary changed |
| Overtime | STEP 6 (Markaz) | CHANGES monthly |
| Commute Allowance | STEP 3 (Commute sheet) | CHANGES monthly |
| Pending Dues | STEP 7 (User input) | CHANGES monthly |

**Components That Usually Stay Same:**
- Gross, Basic, Medical, Other Allowance (unless STEP 5 salary change occurred)

**Components That Change Monthly:**
- ⚠️ Overtime (varies by approvals)
- ⚠️ Commute Allowance (varies by eligibility)
- ⚠️ Pending Dues (varies by situation)

**CRITICAL - Must Calculate Fresh Each Month:**
Do NOT copy previous month's total allowance. Must recalculate using CURRENT month's values because overtime, commute, and pending dues change.

**Step-by-Step Process for Each Employee:**

1. Get Gross Salary from payroll
2. Get Basic Salary from payroll
3. Get Medical Allowance from payroll
4. Get Other Allowance from payroll
5. Get Overtime amount from STEP 6 (may be 0)
6. Get Commute Allowance from STEP 3 (may be 0)
7. Get Pending Dues from STEP 7 (may be 0)
8. **Add all 7 values together**
9. Enter result in "Total Allowance" column

**Verification:**
- ✅ Check addition is mathematically correct
- ✅ No values skipped or doubled
- ✅ Total is reasonable for employee level
- ✅ Overtime only included if approved (STEP 6)
- ✅ Commute only included if eligible (STEP 3)
- ✅ Pending dues only included if provided (STEP 7)

**Example Calculation:**

```
Employee: Muhammad Ali (NIETE ICT, Grade B)

Gross Salary:            100,000
Basic Salary:             70,000
Medical Allowance:         5,000
Other Allowance:           3,000
Overtime (STEP 6):         2,500  (8 hours approved)
Commute Allowance (STEP 3): 2,000  (CPD Coach)
Pending Dues (STEP 7):      5,000  (Salary correction)
──────────────────────────────────
Total Allowance:         187,500
```

**Why Real-Time Addition Every Month:**
- Overtime changes based on monthly approvals
- Commute allowance changes based on role changes
- Pending dues are situational and vary
- Therefore, total cannot be same as previous month
- Must add fresh each time

**⚠️ CRITICAL NOTES:**
- Do NOT copy previous month's total
- Must calculate for EACH employee separately
- Accuracy is important - payroll depends on this
- Include 0 values if employee has no overtime/commute/pending

### STEP 9: Calculate Taxable Salary ✅

**Purpose:** Calculate taxable salary for each employee using standard formula

**Taxable Salary Formula:**
```
Taxable Salary = Total Allowance - Unpaid Days - Medical Allowance
```

**Three Components in Formula:**

| Component | Source | Notes |
|-----------|--------|-------|
| Total Allowance | STEP 8 | Sum of all 7 allowance components |
| Unpaid Days | STEP 2 | Deduction for mid-month joiners (may be 0) |
| Medical Allowance | STEP 1 or STEP 5 | Usually tax-exempt portion of salary |

**How Each Component Works:**

**Component 1: Total Allowance (from STEP 8)**
- Full amount calculated in previous step
- All 7 components included (gross, basic, medical, other, overtime, commute, pending)

**Component 2: Unpaid Days (from STEP 2)**
- Deduction for employees joining mid-month (5th onwards)
- Calculated when employee joins between 5th-23rd of month
- Formula: (Gross ÷ 30) × Unpaid Days
- If employee joined early or full month = 0
- If employee joined 24th+ = goes to pending dues instead (so unpaid days = 0)

**Component 3: Medical Allowance**
- Portion of salary usually exempt from taxation
- Subtracted from total to get taxable amount
- Same value from payroll throughout year (unless salary changed)

**Step-by-Step Calculation for Each Employee:**

```
1. Get Total Allowance (from STEP 8)
2. Get Unpaid Days amount (from STEP 2)
3. Get Medical Allowance (from payroll)
4. Calculate: Total - Unpaid Days - Medical = Taxable
5. Enter Taxable Salary in payroll
```

**Example 1: Mid-Month Joiner with Unpaid Days**

```
Employee: Fatima Khan
Joining Date: 5th March 2026

Total Allowance (STEP 8):        100,000
Less: Unpaid Days (STEP 2):      -14,000  (4 days unpaid × 3,500 per day)
Less: Medical Allowance:          -5,000  (tax-exempt)
────────────────────────────────────────
Taxable Salary:                   81,000
```

**Example 2: Full Month Employee (No Unpaid Days)**

```
Employee: Muhammad Ali
Employment: Full month

Total Allowance (STEP 8):        187,500
Less: Unpaid Days:                   0    (no unpaid days)
Less: Medical Allowance:          -5,000
────────────────────────────────────────
Taxable Salary:                  182,500
```

**Example 3: Late Month Joiner (24th+)**

```
Employee: Ahmed Hassan
Joining Date: 25th February 2026

Total Allowance (STEP 8):         30,000  (pending dues only, added next month)
Less: Unpaid Days:                    0   (no unpaid days - goes to pending dues)
Less: Medical Allowance:           0      (not applicable for partial month)
────────────────────────────────────────
Taxable Salary:                   30,000  (for future month when added)
```

**Key Points:**
- ✅ Applied to EVERY employee
- ✅ Each gets individual taxable salary
- ✅ Monthly calculation
- ✅ Used for tax deduction calculations
- ✅ Different from Gross Salary (which is full salary)

**Verification:**
- Check subtraction is correct
- Ensure no component is skipped
- Taxable should be less than or equal to Total Allowance
- Unpaid days only non-zero for mid-month joiners

**⚠️ IMPORTANT:**
- Taxable Salary is different from Gross Salary
- Used specifically for tax calculations
- Medical allowance is excluded from taxation
- Unpaid days reduce taxable amount

### STEP 11: Add Advance Salary Deductions ✅

**Purpose:** Track and deduct employee salary advances from current month payroll

**Advance Salary Workflow:**
1. Employee requests advance through Taleemabad Markaz (People and Culture → Loans and Advances)
2. HR approves the request
3. Finance releases the advance salary to employee
4. Finance team deducts this advance from next payroll

**Data Sources - DUAL VERIFICATION (Always verify both):**

**Source 1: Taleemabad Markaz (Live System)**
- **Link:** https://markaz.taleemabad.com/overtime-loans-advances
- **Path:** People and Culture → Loans and Advances
- **Contains:** Live advance requests with approval status and finance release status

**Source 2: Advances Tracking Sheet (Reference/Verification)**
- **Link:** https://docs.google.com/spreadsheets/d/1sxXfGghw1cGuTsP15VZMxXCxkT1SxY61UNmHMp6vtBE/edit?gid=0#gid=0
- **Tab:** Advances (first tab)
- **Contains:** Employee Name, Month (advance taken for), Notes, Amount
- **Purpose:** Cross-verify against Markaz to ensure accuracy

**Verification Process:**

1. Open Advances Tracking Sheet
2. Find all entries for current month
3. For EACH employee with advance:
   - Note the employee name
   - Note the advance amount (can be full salary or partial)
   - Cross-verify in Taleemabad Markaz (optional verification step)
   - If amounts differ between sources → Stop and verify which is correct
4. Add verified amount to payroll → "Advance" column

**Amount Types:**

- **Full Salary:** Employee took their entire gross salary as advance
  - Example: "Full Salary" or "PKR 405,696" (full month salary)
  - Action: Add the full gross salary amount to "Advance" column
  
- **Partial Amount:** Employee took only part of their salary as advance
  - Example: "PKR 100,000" or "PKR 50,000"
  - Action: Add exact amount shown to "Advance" column

**Special Cases:**

**Case 1: Employee Already Received Advance, Hold Next Month**
- Example: Danish Iqbal (May/June entry)
- Notes: "He took his May salary as an advance but unfortunately we disbursed his May's salary. So we will be holding his June's salary."
- Action: In June payroll, do NOT pay salary (entire amount goes to "Advance" repayment)
- This is noted in the tracking sheet — follow HR/Finance instructions

**Case 2: Partial Advance (Medical/Emergency)**
- Example: Mehdi Abbas (June): "Requested for medical advance of Rs. 50,000"
- Action: Add PKR 50,000 to "Advance" column (not full salary)

**Case 3: Full Salary Advance**
- Example: Sana Nawaz (April 2026): "Taking full salary as advance"
- Amount: PKR 92,482 (her full gross salary that month)
- Action: Add PKR 92,482 to "Advance" column

**Data Entry Steps:**

1. Get current month from processing month
2. Search Advances Tracking Sheet for all rows matching current month
3. For EACH matching row:
   - Extract employee name
   - Extract amount (PKR value, ignore text like "PKR" or "Full Salary" label)
   - Verify 4-step employee verification (name, ID, entity, details)
   - Add amount to "Advance" column in payroll
4. Document which employees had advances and amounts

**Example - April 2026 Processing:**

```
From Advances Tracking Sheet:

Zeshan Ali Dhillon    April 2026    Full salary    PKR 405,696
→ Add to payroll: Advance = 405,696

Moiz Khan             April 2026    Partial        PKR 108,945
→ Add to payroll: Advance = 108,945

Fatima Khan           April 2026    Partial        PKR 20,000
→ Add to payroll: Advance = 20,000

(Continue for all April 2026 entries)
```

**⚠️ CRITICAL NOTES:**
- ✅ Always use Advances Tracking Sheet as primary reference
- ✅ Verify from Markaz if amounts seem unclear
- ✅ Use exact PKR amounts shown (convert if "Full Salary" label used)
- ✅ One entry per employee per month only
- ✅ 4-step employee verification required before adding
- ✅ Document which employees had advances deducted
- ✅ Advances are DEDUCTIONS (reduce net salary)

### STEP 15: Calculate Total Deductions ✅

**Purpose:** Sum all 8 deduction components to get total amount deducted from employee's salary

**Total Deductions Formula:**
```
Total Deductions = IT + Unpaid Days + Abhi + Advance + Loan + BusCaro + Lunch + EOBI
```

**8 Deduction Components to Sum:**

| # | Component | Source | Notes |
|---|-----------|--------|-------|
| 1 | IT | STEP 10 | Income Tax (lookup from TAX DEDUCTION DETAILS) |
| 2 | Unpaid Days | STEP 2C | Amount for joining/leaving mid-month |
| 3 | Abhi | STEP 15A | Insurance/benefit deduction (TBD) |
| 4 | Advance | STEP 11 | Salary advance from employee request |
| 5 | Loan | STEP 12 | Monthly loan installment |
| 6 | BusCaro | STEP 13 | Commute service (employee 40% share) |
| 7 | Lunch | STEP 4 | Meal deduction (5,720 fixed for NIETE ICT) |
| 8 | EOBI | STEP 14 | Statutory benefit (370 fixed, except interns) |

**Process for Each Employee:**

1. Get value from IT column (STEP 10)
2. Get value from Unpaid Days column (STEP 2C) — may be 0
3. Get value from Abhi column (STEP 15A) — to be documented
4. Get value from Advance column (STEP 11) — may be 0
5. Get value from Loan column (STEP 12) — may be 0
6. Get value from BusCaro column (STEP 13) — may be 0
7. Get value from Lunch column (STEP 4) — may be 0 (NIETE ICT only)
8. Get value from EOBI column (STEP 14) — 370 or 0 if intern
9. **Add all 8 values together**
10. Enter result in "Total Deductions" column

**Verification:**
- ✅ All 8 values are correct (from previous steps)
- ✅ Addition is mathematically accurate
- ✅ No values skipped or doubled
- ✅ Result is reasonable for employee level
- ✅ If deduction is larger than allowance, flag for review

**Example Calculation:**

```
Employee: Muhammad Ali

Income Tax (IT)                12,500  (from STEP 10)
Unpaid Days                        0   (no unpaid days)
Abhi                            ?      (from STEP 15A)
Advance                        50,000  (from STEP 11)
Loan                            8,000  (from STEP 12)
BusCaro                         9,822  (from STEP 13)
Lunch                           5,720  (from STEP 4)
EOBI                              370  (from STEP 14)
───────────────────────────────────────
Total Deductions               86,412  ← Enter in payroll
```

**Another Example (No Deductions Except Fixed):**

```
Employee: Ayesha Khan

Income Tax (IT)                 8,000
Unpaid Days                        0
Abhi                               0
Advance                            0
Loan                               0
BusCaro                            0
Lunch                              0
EOBI                             370
───────────────────────────────────────
Total Deductions                8,370
```

**Example with All Deductions:**

```
Employee: Hassan Ahmed

Income Tax (IT)                15,000
Unpaid Days                     3,500  (joined late)
Abhi                            2,000
Advance                        75,000
Loan                           10,000
BusCaro                         7,500
Lunch                           5,720
EOBI                              370
───────────────────────────────────────
Total Deductions              118,690
```

**⚠️ CRITICAL NOTES:**
- ✅ Add ALL 8 values (use 0 if component not applicable)
- ✅ Order doesn't matter for addition, but list shows standard order
- ✅ Calculate fresh for EACH employee
- ✅ No rounding — use exact amounts
- ✅ Total Deductions reduces employee's take-home pay

### STEP 10: Add Income Tax (IT) Deduction ✅

**Purpose:** Add monthly income tax (IT) deduction for each employee using pre-calculated reference table

**Reference Sheet:** TAX DEDUCTION DETAILS Sheet (Monthly Breakdown)
**Link:** https://docs.google.com/spreadsheets/d/1nw09utC0x3WFsTEM2Qj548y289FUoccPTW3jft3LeFs/edit?gid=1817370321#gid=1817370321

**CRITICAL: This is a LOOKUP operation, NOT a calculation operation.**

Your finance team pre-calculates all annual income tax based on Pakistan tax slabs, then distributes the liability across 12 months (Jul-Jun financial year). You simply look up the amount for the current month.

---

### How the Finance Team's Tax System Works

**Tax Slab Structure (Pakistan 2025-2026):**
Your finance team uses 6 tax slabs for annual tax calculation:
- **BTL** (Below Tax Limit): 0 to 600,000 → 0% tax
- **Slab 1**: Up to 600,000 → 0% rate
- **Slab 2**: 600,001 to 1,200,000 → 1% rate, no fixed tax
- **Slab 3**: 1,200,001 to 2,200,000 → 11% rate, 6,000 fixed tax
- **Slab 4**: 2,200,001 to 3,200,000 → 23% rate, 116,000 fixed tax
- **Slab 5**: 3,200,001 to 4,100,000 → 30% rate, 346,000 fixed tax
- **Slab 6**: 4,100,001+ → 35% rate, 616,000 fixed tax

**Annual Tax Calculation Formula:**
```
Annual IT = Fixed Tax (for slab) + (Taxable Salary - Slab Minimum) × Slab Rate
```

**Monthly Distribution:**
Once annual IT is calculated, finance team distributes it across the financial year (Jul-25 through Jun-26) based on employee's working months and any tax adjustments.

**Result:** TAX DEDUCTION DETAILS sheet contains monthly breakdown for every employee

---

### STEP 10 Process: Monthly IT Lookup

**Reference Sheet Layout:**

The TAX DEDUCTION DETAILS sheet has:
- Employee names and entities in rows
- Monthly columns: JUL, AUG, SEP, OCT, NOV, DEC, JAN, FEB, MAR, APR, MAY, JUN
- IT deduction amount for each employee for each month
- Total column showing annual IT liability
- Negative amounts (in parentheses) showing tax credits or refunds
- Blank cells for months with no deduction or after employee leaves

**Step-by-Step Process:**

1. **Open TAX DEDUCTION DETAILS sheet** (link above)
2. **Find current month column** (e.g., APRIL for April 2026)
3. **For EACH employee in payroll:**
   - Locate employee name in sheet
   - Find the value in current month column
   - If blank: Employee has 0 IT deduction for this month
   - If positive number: Add to "Income Tax" column in payroll
   - If negative (in parentheses): This is a tax credit/refund - enter as negative value
4. **Enter exact amount** in payroll → "Income Tax" column
5. **Document** which employees had IT deductions or credits

---

### Special Cases

**Case 1: Negative Amount (Tax Credit/Refund)**

When employee is over-deducted in previous months, negative IT appears (shown in parentheses):
- Example: Employee shows (5,000) for current month
- Action: Enter as -5,000 in payroll (reduces deduction or adds credit)
- This reduces total deductions that month

**Case 2: Blank Cell (No IT Deduction)**

When employee has blank IT for a month:
- Example: New joiner starting mid-month
- Action: No IT entry (leave IT column blank or 0)
- Reason: Finance team calculated 0 for this month

**Case 3: Employee Leaves During Year**

When employee exits/resigns mid-financial year:
- Example: Employee leaves April, no IT in May/Jun columns
- Action: Skip that employee for remaining months
- Reason: Finance team only calculates IT for working months

---

### Data Verification (Before Adding IT)

**Verification Steps for Each Employee:**

1. **Verify employee exists in payroll**
   - Find exact name match in payroll sheet
   - Match spelling exactly - no variations
   
2. **Verify employee exists in TAX DEDUCTION DETAILS**
   - Locate same employee name in reference sheet
   - Should be in same entity section
   
3. **Verify amount is correct**
   - Cross-check the amount shown for current month
   - Confirm it matches finance team's reference sheet exactly
   
4. **Handle special characters/formatting**
   - Negative amounts: Enter with minus sign (-5,000)
   - Decimal amounts: Enter as shown (e.g., 8,250)
   - Blank cells: Leave as 0 or empty

**If Employee Not Found in Reference Sheet:**
- Verify name spelling in payroll
- Check if employee should have IT (not on payroll for this month?)
- Ask user if employee is missing from reference sheet
- Do NOT guess or assume IT amount

---

### Example: April 2026 Monthly IT Additions

```
Reference Sheet (TAX DEDUCTION DETAILS - APR column):

Employee Name         | APR Amount
─────────────────────────────────
Muhammad Ali          | 12,500
Fatima Khan          | 8,250
Ahmed Hassan         | (5,000)    ← Tax credit/refund
Sarah Ahmed          | 15,700

Action: Add these exact amounts to April payroll IT column
- Muhammad Ali: 12,500
- Fatima Khan: 8,250
- Ahmed Hassan: -5,000 (negative/credit)
- Sarah Ahmed: 15,700
```

---

### CRITICAL NOTES

- ✅ **LOOKUP ONLY** — Do NOT calculate IT yourself
- ✅ **Use exact amounts** — Finance team has pre-calculated everything
- ✅ **Financial year basis** — Jul-Jun, not calendar year
- ✅ **Verify employee match** — Spelling must be exact
- ✅ **Handle negatives carefully** — Tax credits shown as negative
- ✅ **Blank = 0** — No deduction that month
- ✅ **One entry per month** — Only add current month's IT

**Why This Approach:**
- Removes calculation errors
- Uses finance team's official methodology
- Ensures consistency across all payroll
- YTD tracking already done by finance team
- Your role is verification and accurate data entry only

### Timeline
- [ ] Attendance submission deadline
- [ ] Payroll sheet creation deadline
- [ ] Approval workflow timeline
- [ ] Payment processing date

### Roles & Responsibilities
- [ ] Who submits attendance
- [ ] Who approves payroll
- [ ] Who processes payments
- [ ] Who audits payroll

## Salary Components
(To be documented)

### Compensation Structure
- [ ] Basic salary
- [ ] Allowances (if applicable)
- [ ] Deductions (if applicable)
- [ ] Bonuses/incentives (if applicable)

## Approvals & Sign-offs
(To be documented)

## Audit Trail
(To be documented)

## Related
- See payroll/memory.md for accumulated learnings
- See payroll/docs/ for API references
