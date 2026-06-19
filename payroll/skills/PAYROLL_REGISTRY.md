# Payroll Sheet Registry
**Last updated: 2026-05-04**

This file is the single source of truth for payroll Google Sheet IDs.
Update this file monthly when a new payroll sheet is finalized.
The salary-docs.md skill references this registry – do not hardcode sheet IDs elsewhere.

---

## FY 2025-26 Payroll Sheets

| Month | Sheet Title | Sheet ID | Google Sheets Link |
|-------|-------------|----------|--------------------|
| July 2025 | Copy of Payroll July 2025 Revised | `1I2t3hMpKqr96v8Ng_RgkI8jrTCh0E06wpNAKujxmvU8` | [Open](https://docs.google.com/spreadsheets/d/1I2t3hMpKqr96v8Ng_RgkI8jrTCh0E06wpNAKujxmvU8/edit) |
| August 2025 | Copy of Payroll August-2025-Revised | `1ER8V3EYgsDTtOXCuhZRVBey7q2xebM07OKuNqiWlgmU` | [Open](https://docs.google.com/spreadsheets/d/1ER8V3EYgsDTtOXCuhZRVBey7q2xebM07OKuNqiWlgmU/edit) |
| September 2025 | Copy of Payroll September 2025 Revised | `1VOucWkJJZqg99jlJLBX87oIPfF2rmuWOYSsOgaW3Pds` | [Open](https://docs.google.com/spreadsheets/d/1VOucWkJJZqg99jlJLBX87oIPfF2rmuWOYSsOgaW3Pds/edit) |
| October 2025 | Copy of Payroll October 2025 - Revised Final | `1GDrEq69qv1bCKuL-Zivd_lIXnqJ0a17ED2QWvGRLXFA` | [Open](https://docs.google.com/spreadsheets/d/1GDrEq69qv1bCKuL-Zivd_lIXnqJ0a17ED2QWvGRLXFA/edit) |
| November 2025 | Payroll November 2025 Revised | `1NHnjvsJc-hk9l7qQvOTQr3znKFPzjc9mEBbtKWmJjjA` | [Open](https://docs.google.com/spreadsheets/d/1NHnjvsJc-hk9l7qQvOTQr3znKFPzjc9mEBbtKWmJjjA/edit) |
| December 2025 | Payroll December 2025 Revised | `1FprPYHx-S_RaV-C5HGGENg3BVeWzhmn3eUx1Ofuk7gk` | [Open](https://docs.google.com/spreadsheets/d/1FprPYHx-S_RaV-C5HGGENg3BVeWzhmn3eUx1Ofuk7gk/edit) |
| January 2026 | Payroll January 2026 Revised | `1EXJhbbqI952ick9-VhSX3k6MxC6oGSVeg9NJfrlYqeI` | [Open](https://docs.google.com/spreadsheets/d/1EXJhbbqI952ick9-VhSX3k6MxC6oGSVeg9NJfrlYqeI/edit) |
| February 2026 | Payroll February 2026 Revised | `1v-vLLvij1phN_havWvGzbOWaz1apQcs3unHAectyTdY` | [Open](https://docs.google.com/spreadsheets/d/1v-vLLvij1phN_havWvGzbOWaz1apQcs3unHAectyTdY/edit) |
| March 2026 | Payroll March 2026 | `1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk` | [Open](https://docs.google.com/spreadsheets/d/1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk/edit) |
| April 2026 | Payroll April 2026 | `1OUR1Bj9aqF1JekArcfqmlE3nP9kBHqMfJZWJuo3kK8E` | [Open](https://docs.google.com/spreadsheets/d/1OUR1Bj9aqF1JekArcfqmlE3nP9kBHqMfJZWJuo3kK8E/edit) |

---

## How to Add a New Month

1. Get the finalized payroll sheet link from the HR team.
2. Extract the sheet ID from the URL: `https://docs.google.com/spreadsheets/d/**{SHEET_ID}**/edit`
3. Add a new row to the table above.
4. Update the "Last updated" date at the top.

---

## Tab Search Rule (CRITICAL)

**Always scan ALL tabs in a sheet for every employee lookup.**
Never pre-assign a tab (e.g. "OPL", "NIETE_Islamabad") to an employee.

Tab names change across months (e.g. `NIETE-ICT` in July 2025 – `NIETE_Islamabad` from August 2025).
Skip only obviously non-payroll tabs: "Appraisal Outcome", "Sheet1", "Summary", etc.

Match priority:
1. Match by Employee ID first
2. Fall back to Employee Name (case-insensitive, partial match)
