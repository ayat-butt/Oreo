# March 2026 Tax Working Sheet Extraction Summary

## Files Generated
- `MARCH_2026_TAX_DATA_FOR_APRIL_DEDUCTIONS.csv` - Main data file with all 147 active employees

## Data Source
- **Source**: March 2026 Tax Working Sheet (Google Sheet ID: 1nw09utC0x3WFsTEM2Qj548y289FUoccPTW3jft3LeFs)
- **Sheet Used**: "Tax Calculation" 
- **Total Employees**: 147 active employees extracted (inactive employees excluded)
- **Extracted Date**: April 28, 2026

## Column Definitions

| Column | Source Sheet Column | Description |
|--------|-------------------|-------------|
| **Employee Name** | B | Full name of employee |
| **Entity** | C | Organization/Company (NIETE, OPL, OWT, Digital Learning, Executive) |
| **YTD Taxable (Jul-Feb)** | M | Cumulative tax COLLECTED from July 2025 through February 2026 (8 months) |
| **Mar 2026 Taxable** | O | Calculated tax deduction for March 2026 |
| **Annual Taxable (Projected)** | D | Estimated annual taxable salary for full 12-month year |
| **Annual Tax Liability (FBR)** | L | Total FBR income tax liability for the entire year |
| **Tax Collected So Far (Jul-Feb)** | M | Same as YTD Taxable - cumulative tax from 8 months |

## Important Notes

### Tax Formula for April 2026 Deduction
```
April 2026 Tax = (Annual Tax Liability - Tax Collected Jul-Mar) / 3
                = (Annual Tax Liability - (Tax Col Jul-Feb + Mar Tax)) / 3
```

### Data Interpretation
1. **"YTD Taxable (Jul-Feb)"** is NOT the taxable salary amount - it is the CUMULATIVE TAX AMOUNT deducted from 8 months of salary
2. **"Annual Taxable (Projected)"** is the estimated annual taxable salary (12 months)
3. **"Annual Tax Liability (FBR)"** is calculated based on tax slabs for the annual salary
4. **"Mar 2026 Taxable"** represents the calculated tax amount for March based on the tax calculation sheet

### Tax Slabs Used (2025-2026)
- Below 600,000: No tax (BTL)
- 600,001 - 1,200,000: 1% tax
- 1,200,001 - 2,200,000: 6,000 + 11% on excess
- 2,200,001 - 3,200,000: 116,000 + 23% on excess
- 3,200,001 - 4,100,000: 346,000 + 30% on excess
- 4,100,001+: 616,000 + 35% on excess

## Employees with No Tax Data
The following employees have "-" values, indicating no tax liability:
- Aown Raza
- Umair Munir Khan
- Syed Zaamin Abbas
- Zaigham Abbas
- Muhammad Shoaib Khan
- Razia Kausar
- Zulfiqar Ahmed Mughal
- Haroon Ali
- Sabeena Abbasi

These employees likely fall below the tax threshold (annual salary < 600,000)

## Employees Included
All 147 active employees from the Tax Calculation sheet are included. This includes employees across all entities:
- NIETE (largest group)
- OPL
- OWT
- Digital Learning
- Executive (small group)

## Data Quality
- Some rows have formatting inconsistencies (e.g., "Babar Khan", "Hassan Shahzad", "Saleh Muhammad" have incomplete/misaligned data)
- Negative values in "Mar 2026 Taxable" indicate potential tax refunds or adjustments
- All data is as of the most recent update in the Tax Working Sheet

## Next Steps for April Payroll
1. Match each employee to April 2026 payroll by name
2. For each employee, calculate April 2026 tax as: (Annual Tax Liability - Tax Collected Jul-Mar) / 3
3. Ensure employees not in this tax data are handled separately
4. Review employees with negative values for special handling
