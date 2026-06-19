# Income Tax Calculation — Reference Documentation

**Purpose:** BACKGROUND REFERENCE ONLY — Shows how finance team calculates annual IT (you use LOOKUP-based STEP 10 instead)

**🔴 CRITICAL:** Your STEP 10 implementation is LOOKUP-based, NOT calculation-based. This file explains the finance team's methodology for reference/understanding only. Do NOT calculate IT yourself — use TAX DEDUCTION DETAILS sheet for monthly amounts.

**Status:** Reference methodology locked in — STEP 10 implementation is lookup-based (see payroll/context/payroll-procedures.md)

---

## Pakistan Income Tax Slabs (2025-2026)

| Slab | Taxable Salary Range | Fixed Tax | Slab Rate |
|------|----------------------|-----------|-----------|
| BTL | Below 600,000 | — | 0% |
| 1 | 600,001–1,200,000 | — | 1% |
| 2 | 1,200,001–2,200,000 | 6,000 | 11% |
| 3 | 2,200,001–3,200,000 | 116,000 | 23% |
| 4 | 3,200,001–4,100,000 | 346,000 | 30% |
| 5 | 4,100,001+ | 616,000 | 35% |

**Source:** Google Sheet (ID: 1nw09utC0x3WFsTEM2Qj548y289FUoccPTW3jft3LeFs)  
**Date Locked In:** 2026-04-17

---

## How to Calculate Income Tax

### Algorithm

For each employee's **Taxable Salary**:

1. **Find the correct slab** — Identify which range the taxable salary falls into
2. **Apply fixed tax** — Use the fixed tax amount for that slab
3. **Calculate slab amount** — Subtract slab minimum from taxable salary
4. **Apply slab rate** — Multiply the result by the slab rate (%)
5. **Total IT** = Fixed Tax + Slab Amount × Rate

### Formula Expression

```
IT Deduction = Fixed_Tax_of_Slab + (Taxable_Salary - Slab_Min) × Slab_Rate
```

---

## Example Calculations

### Example 1: BTL (Below Tax Limit)
```
Employee: Ahmed Ali
Taxable Salary: 550,000

Analysis:
- Falls in: BTL (< 600,000)
- Fixed Tax: — (none)
- IT Deduction: 0 PKR
```

### Example 2: Slab 1
```
Employee: Fatima Khan
Taxable Salary: 900,000

Analysis:
- Falls in: Slab 1 (600,001–1,200,000)
- Fixed Tax: — (none)
- Amount in slab: 900,000 - 600,001 = 299,999
- IT Deduction: 299,999 × 1% = 3,000 PKR
```

### Example 3: Slab 2
```
Employee: Muhammad Ali
Taxable Salary: 1,800,000

Analysis:
- Falls in: Slab 2 (1,200,001–2,200,000)
- Fixed Tax: 6,000
- Amount in slab: 1,800,000 - 1,200,001 = 599,999
- IT Deduction: 6,000 + (599,999 × 11%) = 6,000 + 65,999 = 71,999 PKR
```

### Example 4: Slab 3
```
Employee: Hassan Khan
Taxable Salary: 2,800,000

Analysis:
- Falls in: Slab 3 (2,200,001–3,200,000)
- Fixed Tax: 116,000
- Amount in slab: 2,800,000 - 2,200,001 = 599,999
- IT Deduction: 116,000 + (599,999 × 23%) = 116,000 + 137,999 = 253,999 PKR
```

---

## Implementation Notes

- **When to Apply:** STEP 9 of payroll workflow (after calculating Taxable Salary)
- **Who It Applies To:** Every employee with positive taxable salary
- **Rounding:** Round to nearest whole number (PKR)
- **Verification:** Always cross-check calculations manually
- **Reference:** Taxable Salary comes from STEP 9 formula: `Total Allowance - Unpaid Days - Medical Allowance`

---

## Quick Reference Table for Manual Lookups

Use this table to quickly verify which slab an employee falls into:

```
Taxable < 600,000        → BTL       → 0% IT
600,001 - 1,200,000      → Slab 1    → 1% IT on amount above 600,001
1,200,001 - 2,200,000    → Slab 2    → 11% IT + fixed 6,000
2,200,001 - 3,200,000    → Slab 3    → 23% IT + fixed 116,000
3,200,001 - 4,100,000    → Slab 4    → 30% IT + fixed 346,000
4,100,001+               → Slab 5    → 35% IT + fixed 616,000
```

---

## ⚠️ IMPORTANT: STEP 10 Implementation

This calculation methodology is **REFERENCE ONLY**. Your actual STEP 10 payroll workflow uses a **LOOKUP-based approach**:

**Finance Team's Role:**
- Calculates annual IT using formulas shown above (for each employee)
- Distributes annual IT across 12 months (Jul-Jun financial year)
- Stores monthly breakdown in TAX DEDUCTION DETAILS sheet
- Handles YTD tracking and tax credits/refunds

**Your Role (STEP 10):**
- Open TAX DEDUCTION DETAILS sheet
- Find current month column
- Lookup exact amount for each employee
- Enter in payroll (no calculations needed)
- Handle negative amounts (tax credits) correctly

**See:** payroll/context/payroll-procedures.md → STEP 10 for actual implementation procedure

---

**Status:** Reference documentation | STEP 10 Implementation is LOOKUP-based  
**Reference Methodology Locked In:** 2026-04-17  
**STEP 10 Lookup Implementation Locked In:** 2026-04-24
