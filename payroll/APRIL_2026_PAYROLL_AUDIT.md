# APRIL 2026 PAYROLL - COMPLETE AUDIT & SETUP

**Source Sheet:** March Payroll Revised 2026  
**Copy Created:** Agent April Payroll 2026  
**Date:** 2026-05-12  
**Status:** READY FOR PROCESSING  

---

## PAYROLL STRUCTURE - 5 ENTITIES

### Entity Breakdown

| # | Entity | Employees | Status | Notes |
|---|--------|-----------|--------|-------|
| 1 | **NIETE_Islamabad** | 84 | Active | Largest entity |
| 2 | **OPL** | 77 | Active | Second largest |
| 3 | **OWT** | 21 | Active | Mid-size |
| 4 | **NIETE_Balochistan** | 1 | Active | Single employee |
| 5 | **Taleemabad_Inc_** | 2 | Active | Executive only |
| | **TOTAL** | **185** | **✓ Verified** | **All Active** |

---

## PAYROLL COLUMNS (26 per entity)

```
1. Employee ID
2. Employee Name
3. Job Title
4. Department
5. CNIC
6. Joining Date
7. Bank Name
8. Account Number
9. Gross Salary
10. Basic Salary
11. Medical Allowance
12. Other Allowance
13. Overtime
14. Commute Allowance
15. Pending Dues
16. Total Allowance
17. Taxable Salary
18. Income Tax
19. Unpaid Days
20. Abhi
21. Advance
22. Loan
23. BusCaro
24. Lunch Meal
25. EOBI
26. Total Deductions
```

**All 26 columns present and consistent across all 5 entities.**

---

## SHEETS CREATED

### March 2026 (Source)
- **ID:** 1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk
- **Status:** Original (Reference)
- **Use:** Read-only reference

### Agent April 2026 (Working Copy)
- **ID:** 1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA
- **Status:** Active (Working)
- **Use:** Modify for April processing
- **Link:** https://docs.google.com/spreadsheets/d/1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA

---

## PAYROLL PROCESSING CHECKLIST

### ✓ Pre-Processing (LOCKED)

- [x] Sheet copied successfully
- [x] All 5 entities present
- [x] 185 employees verified
- [x] 26 columns per entity (consistent)
- [x] Column structure matches March 2026

### ⬜ MANDATORY 7-STEP PROTOCOL (Ready to Execute)

**Step 1: EMPLOYEE VERIFICATION** (4-sub-step, PER EMPLOYEE)
- [ ] Match full name exactly (against Markaz DB)
- [ ] Verify employee ID
- [ ] Confirm entity/company
- [ ] Cross-check other details

**Step 2: GATHER ALL DATA** (From multiple sources)
- [ ] Salary data from sheets
- [ ] Salary changes (from emails/Teams)
- [ ] Pending dues (ask HR - MANDATORY)
- [ ] Overtime approvals (dual-approval check)
- [ ] Attendance/leave data

**Step 3: APPLY MANDATORY FORMULAS** (EXACT ORDER)
- [ ] Basic = Gross × 90%
- [ ] Medical = Basic × 10%
- [ ] Other = Gross - Basic - Medical
- [ ] Total Allowance = sum
- [ ] Taxable = Total Allow - Medical - Unpaid Days
- [ ] Deductions = sum of 8 items
- [ ] Net = Allow - Deduct

**Step 4: CROSS-CHECK CALCULATIONS** (Before saving)
- [ ] Basic + Medical + Other = Gross (±0.50)
- [ ] All 8 deductions itemized
- [ ] Net = Gross - Deductions (math check)
- [ ] Compare vs. March (flag if > 10% change)

**Step 5: MONITOR & APPLY SALARY CHANGES**
- [ ] Check emails for promotions
- [ ] Check Teams for increments
- [ ] Check for part-time transitions
- [ ] Apply ONLY after 4-step verification

**Step 6: DUAL-APPROVAL PROTOCOL** (Overtime only)
- [ ] Manager Status = "APPROVED"
- [ ] HR Status = "Moved to April PAYROLL"
- [ ] Manual calculation cross-check

**Step 7: GENERATE & VALIDATE REPORT**
- [ ] Create payroll/output/April_2026_payroll_final.csv
- [ ] Validate row count = 185
- [ ] All formulas match
- [ ] Final user review BEFORE applying

---

## SAMPLE EMPLOYEES BY ENTITY

### NIETE_Islamabad (84 employees)
- Abdul Waheed (Regional Manager)
- Aleeha Noor (Coach)
- Anam Masood (Regional Manager)
- Aneela Khaliq (Coach)
- ... (80 more employees)

### OPL (77 employees)
- ABDUL AHAD (Engineering Manager)
- Abdul Rehman (Data Analyst)
- ... (75 more employees)

### OWT (21 employees)
- Ahsan Javed (Admin & Operation Manager)
- Ahwaz Akhtar (Data Consultant)
- ... (19 more employees)

### NIETE_Balochistan (1 employee)
- Abdullah Durrani (Program Coordinator)

### Taleemabad_Inc_ (2 employees)
- Sabeena Abbasi (Chief Digital Learning Officer)
- Haroon Yasin (CEO)

---

## CRITICAL PAYROLL RULES (LOCKED FOR THIS PAYROLL)

### Rule 1: NO EMPLOYEE CHANGES
- All 185 employees from March 2026 remain
- No new joiners/leavers for this payroll
- Count verification MANDATORY before processing

### Rule 2: SALARY CHANGES FROM EMAILS/TEAMS ONLY
- Monitor for:
  - Promotions (new salary, effective date)
  - Increments (amount, effective date)
  - Part-time transitions (prorated)
  - Status changes (active/suspended)
- Extract carefully, apply in Step 5

### Rule 3: PENDING DUES PROTOCOL
- **MUST ASK:** "Are there pending dues for April 2026?"
- Manually tracked by HR
- Common: new joiners, retroactive payments
- Ask, verify, add

### Rule 4: OVERTIME APPROVAL VERIFICATION
- Dual-approval MANDATORY
- Manager Status = "APPROVED"
- HR Status = "Moved to April PAYROLL"
- Manual hours × rate verification

### Rule 5: TAX CALCULATION
- Use Tax Calculation sheet from reference system
- Apply formulas exactly (no variations)
- Annual salary = baseline for tax slab
- Monthly deduction = annual liability spread

### Rule 6: CROSS-CHECK BEFORE SAVE
- Basic + Medical + Other = Gross (verify)
- All 8 deductions itemized
- Net = Allowances - Deductions
- Compare vs. March 2026 (flag changes > 10%)

### Rule 7: ZERO TOLERANCE
- One error = affects real salary
- 4-step verification EVERY entry
- Never skip, never assume
- Always ask if unsure

---

## ENTITY ISOLATION NOTES

### NIETE_Islamabad (84)
- Largest entity
- Project-NIETE ICT focus
- Multiple departments
- Full processing priority

### OPL (77)
- Second entity
- Learning Engineering, Data & Impact teams
- Standard processing

### OWT (21)
- Smaller entity
- Multiple departments
- Standard processing

### NIETE_Balochistan (1)
- Single employee: Abdullah Durrani
- Program Coordinator
- Full verification required despite small size

### Taleemabad_Inc_ (2)
- Executive level only
- CEO + CDLO
- Standard processing

---

## NEXT STEPS (WHEN READY)

### Immediate (Before Step 1)
1. ✅ Get "Are there pending dues?" confirmation from HR
2. ✅ Check emails/Teams for salary changes
3. ✅ Prepare overtime approvals list (if any)

### When User Confirms Ready
1. Execute 7-step mandatory protocol
2. Process 185 employees with full verification
3. Apply all formulas with cross-checks
4. Generate April payroll CSV
5. Get final user approval
6. Save to payroll/output/

---

## SHEETS READY FOR PROCESSING

**March 2026 (Reference):**
- 5 entities
- 185 employees
- 26 columns
- ✅ Verified

**Agent April 2026 (Working):**
- Copy of March 2026
- Ready for modifications
- ✅ All data transferred
- ✅ Structure intact

---

## VERIFICATION SUMMARY

| Item | Status | Notes |
|---|---|---|
| Sheet Copy | ✅ Complete | Agent April Payroll 2026 created |
| Entity Count | ✅ 5 entities | NIETE_Islamabad, OPL, OWT, NIETE_Balochistan, Taleemabad_Inc_ |
| Employee Count | ✅ 185 total | 84 + 77 + 21 + 1 + 2 = 185 |
| Column Consistency | ✅ 26 columns | All entities identical structure |
| Data Integrity | ✅ Verified | All employees readable |
| Ready for Processing | ✅ YES | All systems ready |

---

## CRITICAL REMINDERS

⚠️ **PAYROLL ISOLATION ACTIVE**
- All work in payroll/ context ONLY
- Use payroll/memory.md for protocols
- Write to payroll/output/ ONLY
- 7-step protocol is MANDATORY
- Zero tolerance for errors

📋 **MANDATORY BEFORE STEP 1**
- [ ] HR confirms pending dues (ask!)
- [ ] Salary changes collected (emails/Teams)
- [ ] Overtime approvals verified
- [ ] All 185 employees ready for verification

✅ **READY TO START**
- Sheet created and verified
- Structure confirmed
- Data integrity checked
- Waiting for user confirmation to proceed with Step 1

---

**Status:** READY FOR PAYROLL PROCESSING  
**Employees:** 185 (all entities)  
**Sheet:** Agent April Payroll 2026 (1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA)  
**Next Action:** Confirm pending dues → Begin Step 1 Employee Verification
