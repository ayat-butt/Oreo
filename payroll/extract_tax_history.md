# Annual Tax Analysis Plan (FY Jul 2025 - Jun 2026)

## Objective
Extract 9-month tax history (Jul 2025 - Mar 2026) to understand:
1. How much tax each employee has paid so far
2. Annual gross salary estimate
3. Remaining tax to deduct in Apr-May-Jun 2026
4. Impact of salary changes, overtime, commute allowances on tax

## Key Concept
- **Financial Year:** Jul 2025 - Jun 2026 (12 months)
- **Tax Calculation:** Annual based on full-year gross salary
  - 9 months history (Jul-Mar) available
  - Need to forecast remaining 3 months (Apr-Jun)
  - Calculate: Projected Annual Salary × Tax Rate ÷ 12 months
  - Then: Remaining Tax = (Annual Tax ÷ 12) × 3 months - (Tax already deducted)

- **Taxable Salary:** Includes all income EXCEPT Medical Allowance
  - Gross Salary
  - Basic Salary (90% of Gross)
  - Other Allowance
  - Overtime (if any)
  - Commute/Travel Allowance (if any)
  - Pending Dues
  
  EXCLUDES: Medical Allowance

## Data Collection Strategy

### For each month (Jul 2025 - Mar 2026):
1. Load payroll sheet
2. Find Income Tax column
3. For each employee, record:
   - Name
   - Employee ID
   - Monthly Gross Salary
   - Income Tax deducted
   - Any special allowances (overtime, commute, etc.)

### Then calculate:
1. Sum of Income Tax for 9 months per employee
2. Average monthly salary (9 months)
3. Projected annual salary
4. Expected annual tax
5. Remaining tax for Apr-May-Jun

## Implementation Steps

1. **Load July 2025** → Extract employee tax data
2. **Load Aug-Mar 2026** → Append tax data per employee
3. **Build Tax History** → 9-month tracking per employee
4. **Calculate Projections** → Annual salary and tax estimate
5. **Determine April Tax** → Based on financial year calculation
6. **Apply to April 2026** → Update payroll with calculated amounts

## Expected Outcome

For each active employee in April 2026:
- Total tax deducted Jul-Mar: [X amount]
- Projected annual tax: [Y amount]
- Tax remaining for Apr-Jun: [Z amount]
- April 2026 tax deduction: [Z ÷ 3] amount

This will be applied to the April 2026 payroll sheet (Column R: Income Tax)
