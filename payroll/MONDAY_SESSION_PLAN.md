# MONDAY SESSION PLAN — April 2026 Payroll Processing

**Date:** Monday, 2026-04-28  
**Focus:** Resolve authentication → Process April 2026 payroll through all 16 steps

---

## 🔴 PRIORITY 1: Resolve Google Drive Authentication

**Current Status:** OAuth token expired, MCP requires re-authorization

**Choose ONE solution:**

### Solution A: Re-authenticate Through Claude Code IDE (Recommended)
1. Open Claude Code IDE (VS Code with Claude extension)
2. Look for Google Drive connection in settings
3. Click "Re-authorize" or "Reconnect"
4. Complete the OAuth popup
5. Reply "Ready" when done

### Solution B: Set Up Service Account (Most Reliable)
1. Go to: https://console.cloud.google.com/
2. Create new Project ("Payroll Access")
3. Enable Google Drive API
4. Create Service Account → Generate JSON key
5. Share Google Drive folder with service account email
6. Send JSON key file to me

### Solution C: Manual Guided Processing (No Auth Needed)
- Keep sheets open on your screen
- I tell you each step
- You execute the instructions
- Takes slightly longer but requires no authentication

---

## ✅ PRIORITY 2: Process April 2026 Payroll (Once Authenticated)

### Step-by-Step Process:

**STEP 1:** Copy March 2026 → April 2026 payroll sheet  
**STEP 2:** Add/delete employees, calculate unpaid days (Addition/Deletion Tracker)  
**STEP 3:** Add commute allowance (CPD coaches from Commute sheet)  
**STEP 4:** Deduct meal charges (NIETE ICT, 5,720 fixed)  
**STEP 5:** Verify salary components (check for salary changes in Email/Teams)  
**STEP 6:** Add approved overtime (Markaz, dual approval required)  
**STEP 7:** Add pending dues (ask user)  
**STEP 8:** Calculate total allowance (sum 7 components)  
**STEP 9:** Calculate taxable salary (Allowance - Unpaid Days - Medical)  
**STEP 10:** Add Income Tax (lookup from TAX DEDUCTION DETAILS sheet)  
**STEP 11:** Add advances (Advances Tracking sheet - 7 employees data ready)  
**STEP 12:** Add loan installments (Loans tab - need data)  
**STEP 13:** Add BusCaro (user/employee share from routes)  
**STEP 14:** Add EOBI (370 fixed, except interns)  
**STEP 15:** Calculate total deductions (sum 8 components)  
**STEP 16:** Calculate net salary (Allowance - Deductions)  
**VARIANCE:** Document month-to-month changes

---

## 📊 Data Ready

**Already Received:**
- ✅ March 2026 Payroll Sheet (to copy from)
- ✅ Advances Tracking Sheet (April 2026: 7 employees)
  - Zeshan Ali Dhillon: PKR 405,696
  - Moiz Khan: PKR 108,945
  - Sana Nawaz: PKR 92,482
  - Ayat Butt: PKR 50,000
  - Fatima Khan: PKR 20,000
  - Zuhaib Shaikh: PKR 525,000
  - Hamza Razzaq: PKR 139,000

**Still Needed (Monday):**
- Addition/Deletion Tracker (April 2026 new joiners/resignees)
- Loans tab data (monthly installments for April)
- BusCaro April 2026 (routes & user amounts)
- Markaz Overtime data (approved with dual approval)
- Clarification: Abhi (what it is, data source)
- Pending dues confirmation (if any)
- Interns list (to exclude from EOBI)

---

## 📚 Reference Materials Ready

**Complete Documentation:**
- ✅ payroll/context/payroll-procedures.md (all 16 steps + examples)
- ✅ payroll/memory.md (master reference + formulas)
- ✅ payroll/docs/payroll-workflow-summary.md (quick reference)
- ✅ payroll/docs/payroll-processing-checklist.md (monthly template)
- ✅ payroll/SESSIONS.md (session log + status)
- ✅ payroll/CHAT_LOG.md (conversation history)

**All Formulas Locked In:**
```
Unpaid Days = (Gross ÷ 30) × Days
Total Allowance = Gross + Basic + Medical + Other + OT + Commute + Pending
Taxable Salary = Allowance - Unpaid Days - Medical
Total Deductions = IT + Unpaid Days + Abhi + Advance + Loan + BusCaro + Lunch + EOBI
Net Salary = Total Allowance - Total Deductions
Variance = Current Net - Previous Net
```

---

## ⏱️ Estimated Timeline (Once Authenticated)

- **10-15 min:** Gather April 2026 reference data
- **30-45 min:** Process all 16 steps sequentially
- **15-20 min:** Verify calculations & variance analysis
- **Total:** ~1.5-2 hours for complete April 2026 payroll

---

## 🎯 Success Criteria

✅ Google Drive authentication working  
✅ April 2026 payroll sheet created (copy from March)  
✅ All 16 steps processed with accurate data entry  
✅ Employee verification completed (4-step for all entries)  
✅ Variance analysis documented  
✅ Final payroll report generated  
✅ All calculations verified against formulas  

---

## 📞 Questions Before Monday?

If you have any questions about:
- The 16-step process
- The formulas
- The reference sheets
- Authentication options

Feel free to reach out. Everything is documented and ready to go!

---

**See you Monday! 🚀**

*Last Updated: 2026-04-24 EOD*
