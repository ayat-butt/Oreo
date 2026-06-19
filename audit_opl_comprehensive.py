#!/usr/bin/env python3
"""
Comprehensive audit of OPL joiners and leavers
July 2024 - June 2025
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
from datetime import datetime

def load_credentials():
    try:
        with open('token.json', 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired:
            creds.refresh(Request())
        return creds
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_date(date_str):
    """Extract date from various formats"""
    if not date_str or date_str.strip() == '':
        return None

    date_str = date_str.strip()

    # Try various date formats
    formats = ['%d %b %Y', '%d %B %Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except:
            continue
    return date_str  # Return as-is if can't parse

def main():
    creds = load_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)
    spreadsheet_id = '1-GEd1hIU7OOJ-CP97VqnrW1p0TPTXhzDAlgim08HLJM'

    # Define the months to process (July 2024 - June 2025)
    months_to_check = [
        'July, 2024',
        'August, 2024',
        'September, 2024',
        'October 2024',
        'November 2024',
        'Dec 2024',  # Adjust if needed
        'Jan 2025',
        'Feb 2025',
        'March 2025',
        'April 2025',
        'May 2025',
        'June 2025'  # Adjust if needed
    ]

    all_joiners = []
    all_leavers = []
    processed_months = []

    try:
        metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = metadata.get('sheets', [])

        # Create a map of sheet names
        sheet_names = {sheet['properties']['title']: sheet for sheet in sheets}

        print("="*100)
        print("OPL AUDIT: JOINERS & LEAVERS (July 2024 - June 2025)")
        print("="*100)

        for month in months_to_check:
            if month not in sheet_names:
                print(f"\n[WARNING] Sheet '{month}' not found, skipping...")
                continue

            print(f"\n{'-'*100}")
            print(f"Processing: {month}")
            print(f"{'-'*100}")

            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"'{month}'!A1:H100"
            ).execute()

            rows = result.get('values', [])

            # Find sections
            separation_section_start = None
            addition_section_start = None

            for i, row in enumerate(rows):
                if row and len(row) > 0:
                    if 'EMPLOYEE' in str(row[0]).upper() and 'SEPARAT' in str(row[0]).upper():
                        separation_section_start = i
                    elif 'EMPLOYEE' in str(row[0]).upper() and 'ADDITION' in str(row[0]).upper():
                        addition_section_start = i

            # Extract leavers (separations)
            if separation_section_start is not None:
                headers_row = separation_section_start + 1
                if headers_row < len(rows):
                    headers = rows[headers_row]

                    # Find relevant column indices
                    name_col = None
                    entity_col = None
                    separation_date_col = None

                    for col_idx, header in enumerate(headers):
                        header_lower = str(header).lower()
                        if 'name' in header_lower:
                            name_col = col_idx
                        if 'opl' in header_lower or 'owt' in header_lower:
                            entity_col = col_idx
                        if 'separat' in header_lower and 'date' in header_lower:
                            separation_date_col = col_idx

                    # Extract leaver data
                    for row_idx in range(headers_row + 1, len(rows)):
                        row = rows[row_idx]
                        if not row or len(row) == 0:
                            continue
                        if not row[0] or row[0].strip() == '':
                            continue

                        name = row[name_col].strip() if name_col and name_col < len(row) else None
                        entity = row[entity_col].strip() if entity_col and entity_col < len(row) else None
                        sep_date = row[separation_date_col].strip() if separation_date_col and separation_date_col < len(row) else None

                        if entity and entity.upper() == 'OPL' and name:
                            all_leavers.append({
                                'name': name,
                                'month': month,
                                'separation_date': extract_date(sep_date),
                                'entity': entity
                            })
                            print(f"  [LEAVER] {name} (Separation: {sep_date})")

            # Extract joiners (additions)
            if addition_section_start is not None:
                headers_row = addition_section_start + 1
                if headers_row < len(rows):
                    headers = rows[headers_row]

                    # Find relevant column indices
                    name_col = None
                    entity_col = None
                    joining_date_col = None

                    for col_idx, header in enumerate(headers):
                        header_lower = str(header).lower()
                        if 'name' in header_lower:
                            name_col = col_idx
                        if 'opl' in header_lower or 'owt' in header_lower:
                            entity_col = col_idx
                        if 'join' in header_lower and 'date' in header_lower:
                            joining_date_col = col_idx

                    # Extract joiner data
                    for row_idx in range(headers_row + 1, len(rows)):
                        row = rows[row_idx]
                        if not row or len(row) == 0:
                            continue
                        if not row[0] or row[0].strip() == '':
                            continue

                        name = row[name_col].strip() if name_col and name_col < len(row) else None
                        entity = row[entity_col].strip() if entity_col and entity_col < len(row) else None
                        join_date = row[joining_date_col].strip() if joining_date_col and joining_date_col < len(row) else None

                        if entity and entity.upper() == 'OPL' and name:
                            all_joiners.append({
                                'name': name,
                                'month': month,
                                'joining_date': extract_date(join_date),
                                'entity': entity
                            })
                            print(f"  [JOINER] {name} (Joining: {join_date})")

            processed_months.append(month)

        # Generate summary report
        print("\n" + "="*100)  # Summary report header
        print("SUMMARY REPORT")
        print("="*100)

        print(f"\n### JOINERS ({len(all_joiners)} total)")
        print("-"*100)
        if all_joiners:
            for i, joiner in enumerate(all_joiners, 1):
                print(f"{i:2d}. {joiner['name']:<40} | Joining: {joiner.get('joining_date', 'N/A'):<12} | Month: {joiner['month']}")
        else:
            print("No joiners found")

        print(f"\n### LEAVERS ({len(all_leavers)} total)")
        print("-"*100)
        if all_leavers:
            for i, leaver in enumerate(all_leavers, 1):
                print(f"{i:2d}. {leaver['name']:<40} | Separation: {leaver.get('separation_date', 'N/A'):<12} | Month: {leaver['month']}")
        else:
            print("No leavers found")

        print(f"\n### STATISTICS")
        print("-"*100)
        print(f"Total Joiners: {len(all_joiners)}")
        print(f"Total Leavers: {len(all_leavers)}")
        print(f"Net Change: {len(all_joiners) - len(all_leavers)}")
        print(f"Months Processed: {', '.join(processed_months)}")

        # Save to file
        output_file = 'output/OPL_Audit_Jul2024_Jun2025.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*100 + "\n")
            f.write("OPL AUDIT: JOINERS & LEAVERS (July 2024 - June 2025)\n")
            f.write("="*100 + "\n\n")

            f.write(f"### JOINERS ({len(all_joiners)} total)\n")
            f.write("-"*100 + "\n")
            if all_joiners:
                for i, joiner in enumerate(all_joiners, 1):
                    f.write(f"{i:2d}. {joiner['name']:<40} | Joining: {joiner.get('joining_date', 'N/A'):<12} | Month: {joiner['month']}\n")
            else:
                f.write("No joiners found\n")

            f.write(f"\n### LEAVERS ({len(all_leavers)} total)\n")
            f.write("-"*100 + "\n")
            if all_leavers:
                for i, leaver in enumerate(all_leavers, 1):
                    f.write(f"{i:2d}. {leaver['name']:<40} | Separation: {leaver.get('separation_date', 'N/A'):<12} | Month: {leaver['month']}\n")
            else:
                f.write("No leavers found\n")

            f.write(f"\n### STATISTICS\n")
            f.write("-"*100 + "\n")
            f.write(f"Total Joiners: {len(all_joiners)}\n")
            f.write(f"Total Leavers: {len(all_leavers)}\n")
            f.write(f"Net Change: {len(all_joiners) - len(all_leavers)}\n")
            f.write(f"Months Processed: {', '.join(processed_months)}\n")

        print(f"\n[DONE] Report saved to: {output_file}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
