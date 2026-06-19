# April 2026 Tax Deduction Data Package

## Overview
Complete tax data extraction from March 2026 Tax Working Sheet for calculating correct April 2026 income tax deductions using the formula:

**April 2026 Tax = (Annual Tax Liability - Tax Collected Jul-Mar) / 3**

## Files Included

### 1. MARCH_2026_TAX_DATA_FOR_APRIL_DEDUCTIONS.csv
**Primary Data File** - Contains all employee tax information needed for April 2026 payroll

- **Records**: 147 active employees
- **Columns**: 7 key fields
  1. Employee Name
  2. Entity (NIETE, OPL, OWT, etc.)
  3. YTD Taxable (Jul-Feb) - Cumulative tax collected 8 months
  4. Mar 2026 Taxable - Calculated tax for March 2026
  5. Annual Taxable (Projected) - Estimated annual taxable salary
  6. Annual Tax Liability (FBR) - Total annual tax obligation
  7. Tax Collected So Far (Jul-Feb) - Same as YTD

**Use Case**: Import directly into April 2026 payroll calculations

### 2. TAX_EXTRACTION_SUMMARY.md
**Reference Guide** - Detailed explanation of data structure and definitions

- Data source and extraction date
- Column definitions with sheet references
- Tax slab information (2025-2026)
- List of employees with no tax liability
- Data quality notes

### 3. TAX_CALCULATION_EXAMPLES.md
**Calculation Examples** - 5 sample calculations showing how to compute April 2026 tax

- High earner example
- Mid-range earner example
- Low earner example
- No-tax employee example
- Validation checklist

### 4. march_2026_tax_detailed.csv
**Detailed Working File** - Extended version with column name explanations in headers

- Same 147 employees as main file
- Verbose column headers with notes
- Useful for reference and documentation

## Quick Start Guide

### To Calculate April 2026 Tax for Any Employee:

1. Find employee name in MARCH_2026_TAX_DATA_FOR_APRIL_DEDUCTIONS.csv
2. Locate these values:
   - Annual Tax Liability (Column F)
   - Tax Collected Jul-Feb (Column G)
   - Mar 2026 Tax (Column D)
3. Calculate:
   ```
   Remaining Tax = Annual Tax Liability - Tax Jul-Feb - Mar 2026 Tax
   April 2026 Tax = Remaining Tax / 3
   ```
4. Round to 2 decimal places

### Example:
```
Anam Masood:
Annual Tax = 234,014
Less: Jul-Feb = 156,009
Less: Mar Tax = 19,501.32
Remaining = 58,503.68
April Tax = 58,503.68 ÷ 3 = 19,501.23
```

## Data Quality Notes

### Employees with "-" (No Tax)
These 9 employees fall below tax threshold (600,000 annual):
- Aown Raza
- Umair Munir Khan
- Syed Zaamin Abbas
- Zaigham Abbas
- Muhammad Shoaib Khan
- Razia Kausar
- Zulfiqar Ahmed Mughal
- Haroon Ali
- Sabeena Abbasi

**April 2026 Tax for these employees = 0**

### Negative Values
Some employees show negative "Mar 2026 Taxable" values, indicating:
- Tax refunds
- Salary reductions in March
- Adjustments in tax calculations

Examples:
- Mehwish Allah Ditta: (686.53)
- Sumaya Imran: (929.57)
- Abdul Ahad: (542.20)
- Ayesha Jamshaid: (31,062.20)

**Handle these carefully** - they may represent special cases

### Data Inconsistencies
3 employees have incomplete data alignment:
- Babar Khan
- Hassan Shahzad
- Saleh Muhammad

Review these entries in source sheet if exact values needed.

## Source Information

**Data Source**: Google Sheet
- **File**: March 2026 Tax Working Sheet
- **Sheet ID**: 1nw09utC0x3WFsTEM2Qj548y289FUoccPTW3jft3LeFs
- **Sheet Used**: "Tax Calculation" (997785745)
- **Extraction Date**: April 28, 2026
- **Extracted By**: Extraction script (extract_march_tax_refined.py)

## Tax Slabs Reference (2025-2026)

| Annual Taxable | Rate | Fixed Tax | Calculation |
|---|---|---|---|
| Below 600,000 | BTL | - | No tax |
| 600,001 - 1,200,000 | 1% | - | 1% of amount |
| 1,200,001 - 2,200,000 | 11% | 6,000 | 6,000 + 11% of excess |
| 2,200,001 - 3,200,000 | 23% | 116,000 | 116,000 + 23% of excess |
| 3,200,001 - 4,100,000 | 30% | 346,000 | 346,000 + 30% of excess |
| 4,100,001+ | 35% | 616,000 | 616,000 + 35% of excess |

## Validation Steps Before Using

1. **Employee Count**: Verify all 147 employees are in April 2026 payroll
2. **Name Matching**: Check for spelling variations or name changes
3. **Missing Employees**: Identify any April payroll employees NOT in this data
4. **New Joiners**: Confirm if any new employees joined in Apr 2026 (not in this data)
5. **Salary Changes**: Check for salary changes announced in Apr 2026 emails/Teams
6. **Entity Verification**: Confirm each employee's entity matches records
7. **Tax Amounts**: Cross-check high earners and no-tax employees

## Integration with April 2026 Payroll

1. **Import**: Load MARCH_2026_TAX_DATA_FOR_APRIL_DEDUCTIONS.csv into payroll system
2. **Match**: Link employees by name to April 2026 employee records
3. **Calculate**: Apply formula for each matched employee
4. **Handle Unmatched**: Review employees in April payroll NOT in tax data
5. **Review**: Compare calculated values with expected ranges
6. **Approve**: Get Ayat's approval before finalizing tax amounts

## Support & Questions

For questions about:
- **Data Source**: Check TAX_EXTRACTION_SUMMARY.md
- **Calculations**: See TAX_CALCULATION_EXAMPLES.md
- **Specific Employee**: Check MARCH_2026_TAX_DATA_FOR_APRIL_DEDUCTIONS.csv
- **Tax Slabs**: Refer to tax slab reference table above

## Version History

- **v1.0** - April 28, 2026 - Initial extraction from March 2026 Tax Working Sheet
- Extract covers 147 active employees
- 9 employees with no tax liability
- Based on Tax Calculation sheet with data through March 2026
