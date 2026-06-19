#!/usr/bin/env python3
"""
Create FINAL OPL Joiners and Leavers Sheet
Based on comprehensive July 2024 - June 2025 payroll analysis
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

def load_credentials():
    try:
        with open('token.json', 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired:
            creds.refresh(Request())
        return creds
    except:
        return None

def main():
    creds = load_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)

    # Data compiled from comprehensive payroll analysis
    # Format: (name, department, designation, joining_month, leaving_month, salary, joining_date_detail, leaving_date_detail)

    data_entries = [
        # Opening - November 2024 Joiners
        ("ABDULREHMAN SIDDIQI", "CEO & Directors / Operation Department / Marketing Team", "", "November 2024", "", "163281", "November 2024", ""),
        ("AQIB MEHMOOD SATTI", "CEO & Directors / Operation Department / Customer Success Team", "", "November 2024", "", "122100", "November 2024", ""),
        ("Abdur Rehman", "CEO & Directors / Product & Design Engineering / Product Team", "Product & Data Analytic Manager", "November 2024", "February 2025", "236610", "November 2024", "31st January 2025"),
        ("Abdurrehman Afridi", "CEO & Directors / Product & Design Engineering / Engineering team", "Backend Developer", "November 2024", "February 2025", "176100", "November 2024", "31st January 2025"),
        ("Ahmed Javed", "", "", "November 2024", "January 2025", "445900", "November 2024", "31st December 2024"),
        ("Ajlal Hasan", "CEO & Directors / Product & Design Engineering / Engineering team", "Odoo Developer", "November 2024", "February 2025", "151620", "November 2024", "31st January 2025"),
        ("Aleena Athar", "CEO & Directors / Product & Design Engineering / Product Team", "Senior Product Manager", "November 2024", "February 2025", "192075", "November 2024", "31st January 2025"),
        ("Amina Tayyab", "", "", "November 2024", "January 2025", "192075", "November 2024", "31st December 2024"),
        ("Aroma Tahir", "CEO & Directors / Operation Department / Marketing Team", "Brand and Marketing Manager", "November 2024", "February 2025", "170000", "November 2024", "31st January 2025"),
        ("Ayesha Ehtisham", "CEO & Directors / Product & Design Engineering / Engineering team", "AI Engineer", "November 2024", "February 2025", "153660", "November 2024", "31st January 2025"),
        ("Babar Khan", "CEO & Directors / Operation Department / Admin Team", "Office Assistant", "November 2024", "February 2025", "37000", "November 2024", "31st January 2025"),
        ("Fahad Mahmood", "", "", "November 2024", "January 2025", "687000", "November 2024", "31st December 2024"),
        ("Fatima Rahman", "CEO & Directors / Product & Design Engineering / Engineering team", "Software Quality Assurance Engineer", "November 2024", "February 2025", "121128", "November 2024", "31st January 2025"),
        ("Hamza Shahid", "Accounts & Finance", "Deputy Manager Accounts & Finance", "November 2024", "February 2025", "170000", "November 2024", "31st January 2025"),
        ("Haroon Yasin", "", "", "November 2024", "January 2025", "723198", "November 2024", "31st December 2024"),
        ("Hassan Ali", "CEO & Directors / Operation Department / Customer Success Team", "Relationship Specialist", "November 2024", "February 2025", "92015", "November 2024", "31st January 2025"),
        ("Hassan Amin", "CEO & Directors / Product & Design Engineering / Product Team", "Product Manager", "November 2024", "February 2025", "124650", "November 2024", "31st January 2025"),
        ("Hassan Ibrahim", "CEO & Directors / Product & Design Engineering / Engineering team", "Software Quality Assurance Engineer", "November 2024", "February 2025", "65000", "November 2024", "31st January 2025"),
        ("Hataf Atif", "CEO & Directors / Product & Design Engineering / Engineering team", "Full Stack Engineer", "November 2024", "February 2025", "0", "November 2024", "31st January 2025"),
        ("Jawwad Ali", "CEO & Directors / Operation Department / HR Department", "People & Culture Manager", "November 2024", "February 2025", "185280", "November 2024", "31st January 2025"),
        ("Laraib Sarfraz", "CEO & Directors / Product & Design Engineering / Engineering team", "Frontend Developer", "November 2024", "February 2025", "0", "November 2024", "31st January 2025"),
        ("MUHAMMAD IMRAN", "CEO & Directors / Product & Design Engineering / Engineering team", "", "November 2024", "January 2025", "60000", "November 2024", "31st December 2024"),
        ("MUHAMMAD JALAL KHAN", "CEO & Directors / Product & Design Engineering / Engineering team", "Frontend Developer", "November 2024", "February 2025", "163783", "November 2024", "31st January 2025"),
        ("MUHAMMAD SAAD BIN IDREES", "CEO & Directors / Product & Design Engineering / Product Team", "Product Manager", "November 2024", "February 2025", "128900", "November 2024", "31st January 2025"),
        ("MUHAMMAD SHOIAB KHAN", "CEO & Directors / Operation Department / Admin Team", "Security Officer", "November 2024", "February 2025", "38570", "November 2024", "31st January 2025"),
        ("Mah Noor", "CEO & Directors / Product & Design Engineering / Engineering team", "Software Quality Assurance Engineer", "November 2024", "February 2025", "135135", "November 2024", "31st January 2025"),
        ("Mahnoor Butt", "CEO & Directors / Operation Department / Customer Success Team", "Customer Success and Operations Specialist", "November 2024", "February 2025", "73600", "November 2024", "31st January 2025"),
        ("Mahnoor Shafique", "CEO & Directors / Product & Design Engineering / Engineering team", "Backend & Dev ops Engineer", "November 2024", "February 2025", "207648", "November 2024", "31st January 2025"),
        ("Mashhood Rastgar", "", "", "November 2024", "January 2025", "688200", "November 2024", "31st December 2024"),
        ("Mateen Sheikh", "", "", "November 2024", "January 2025", "456100", "November 2024", "31st December 2024"),
        ("Mavia", "CEO & Directors / Operation Department / Customer Success Team", "", "November 2024", "January 2025", "88021", "November 2024", "31st December 2024"),
        ("Muhammad Ahsan", "CEO & Directors / Product & Design Engineering / Engineering team", "Senior Angular Developer", "November 2024", "February 2025", "331028", "November 2024", "31st January 2025"),
        ("Muhammad Danish Iqbal", "CEO & Directors / Digital Learning Department", "Manager Content AI", "November 2024", "February 2025", "186975", "November 2024", "31st January 2025"),
        ("Muhammad Kamal", "CEO & Directors / Product & Design Engineering / Engineering team", "Senior Backend Engineer", "November 2024", "February 2025", "314450", "November 2024", "31st January 2025"),
        ("Muhammad Talha", "CEO & Directors / Product & Design Engineering / Engineering team", "Scrum Master", "November 2024", "February 2025", "80000", "November 2024", "31st January 2025"),
        ("Muhammad Zeeshan Usaid", "CEO & Directors / Operation Department / Customer Success Team", "Head of Customer Success & Ops", "November 2024", "February 2025", "222840", "November 2024", "31st January 2025"),
        ("Mujeeb Rehman", "CEO & Directors / Product & Design Engineering / Engineering team", "Senior AI Engineer", "November 2024", "February 2025", "0", "November 2024", "31st January 2025"),
        ("Nabi Ahmad", "CEO & Directors / Product & Design Engineering / Engineering team", "Android Developer", "November 2024", "February 2025", "173040", "November 2024", "31st January 2025"),
        ("Osama Ahmad", "CEO & Directors / Operation Department / Customer Success Team", "Product & Ops Manager", "November 2024", "February 2025", "159159", "November 2024", "31st January 2025"),
        ("Raja Rehan Ahmed", "CEO & Directors / Product & Design Engineering / Engineering team", "Full Stack Developer", "November 2024", "February 2025", "176100", "November 2024", "31st January 2025"),
        ("Ramsha Khurshid", "CEO & Directors / Operation Department / Sales & Growth", "Deputy Head Coach", "November 2024", "February 2025", "256700", "November 2024", "31st January 2025"),
        ("SHEIKH NIMRA", "CEO & Directors / Product & Design Engineering / Engineering team", "Backend Developer", "November 2024", "February 2025", "92586", "November 2024", "31st January 2025"),
        ("SIKANADAR KHURSHID", "CEO & Directors / Operation Department / Customer Success Team", "", "November 2024", "February 2025", "89067", "November 2024", "31st January 2025"),
        ("SYED JUNAID ALI ZAIDI", "CEO & Directors / Operation Department / Marketing Team", "Partnership Manager", "November 2024", "February 2025", "178344", "November 2024", "31st January 2025"),
        ("Sabeena Abbasi", "CEO & Directors / Digital Learning Department", "", "November 2024", "January 2025", "607400", "November 2024", "31st December 2024"),
        ("Saja Abdullah", "CEO & Directors / Product & Design Engineering / Engineering team", "Full Stack Fellow", "November 2024", "February 2025", "200000", "November 2024", "31st January 2025"),
        ("Salwa", "CEO & Directors / Product & Design Engineering / Product Team", "Group Product Manager-Intelligence Vertical", "November 2024", "February 2025", "403000", "November 2024", "31st January 2025"),
        ("Sameer Sheikh", "CEO & Directors / Product & Design Engineering / Product Team", "Data Analyst", "November 2024", "February 2025", "91900", "November 2024", "31st January 2025"),
        ("Sana Akbar", "CEO & Directors / Product & Design Engineering / Engineering team", "Senior Software Quality Assurance Engineer", "November 2024", "February 2025", "240570", "November 2024", "31st January 2025"),
        ("Shayan Ahmad", "CEO & Directors / Operation Department / Sales & Growth", "Partnership Manager", "November 2024", "February 2025", "191555", "November 2024", "31st January 2025"),
        ("Sualeha Anjum", "CEO & Directors / Operation Department / Sales & Growth", "Growth Strategist", "November 2024", "February 2025", "98360", "November 2024", "31st January 2025"),
        ("Summar Raja", "CEO & Directors / Operation Department / HR Department", "People & Culture Manager", "November 2024", "February 2025", "169300", "November 2024", "31st January 2025"),
        ("Syed Kamal Raza Naqvi", "CEO & Directors / Operation Department / Marketing Team", "", "November 2024", "January 2025", "290375", "November 2024", "31st December 2024"),
        ("Tooba Bibi", "CEO & Directors / Digital Learning Department", "", "November 2024", "December 2024", "108806", "November 2024", "30th November 2024"),
        ("Usama Tuqir Wahla", "CEO & Directors / Operation Department / Customer Success Team", "Customer Success Manager", "November 2024", "February 2025", "118700", "November 2024", "31st January 2025"),
        ("Usman Imtiaz", "CEO & Directors / Product & Design Engineering / Engineering team", "Deputy Head Coach", "November 2024", "February 2025", "279533", "November 2024", "31st January 2025"),
        ("Uzma Khan", "CEO & Directors / Product & Design Engineering / Product Team", "Product Manager", "November 2024", "February 2025", "127200", "November 2024", "31st January 2025"),
        ("ZEESHAN BADAR BUKHARI", "CEO & Directors / Product & Design Engineering / Product Team", "", "November 2024", "February 2025", "124650", "November 2024", "31st January 2025"),
        ("Zarmeena Siddiqui", "CEO & Directors / Operation Department / Sales & Growth", "Partnership Manager", "November 2024", "February 2025", "101080", "November 2024", "31st January 2025"),
        ("Zeeshan Zahoor", "CEO & Directors / Operation Department / Admin Team", "Office Assistant", "November 2024", "February 2025", "51771", "November 2024", "31st January 2025"),
        ("Zohaib Hasan Khan", "", "", "November 2024", "January 2025", "606250", "November 2024", "31st December 2024"),
        ("Zuhaib Shaikh", "", "", "November 2024", "January 2025", "39630", "November 2024", "31st December 2024"),
        ("Zunaira Shahid", "CEO & Directors / Product & Design Engineering / Engineering team", "Software Quality Assurance Engineer", "November 2024", "February 2025", "60000", "November 2024", "31st January 2025"),

        # January 2025 Joiners
        ("AbdulRehman Siddiqi", "", "Creative Graphics Designer", "January 2025", "February 2025", "163281", "1st January 2025", "31st January 2025"),
        ("Arooj Mazhar", "", "Program Academic Manager", "January 2025", "February 2025", "170940", "1st January 2025", "31st January 2025"),
        ("Ayesha Tahir", "", "Backend Intern", "January 2025", "February 2025", "40000", "1st January 2025", "31st January 2025"),
        ("Damil Jamil", "", "Frontend Intern", "January 2025", "February 2025", "40000", "1st January 2025", "31st January 2025"),
        ("Jahanzeb Ahmed", "", "Intern", "January 2025", "February 2025", "40000", "1st January 2025", "31st January 2025"),
        ("Mavia Qureshi", "", "Relationship specialist", "January 2025", "February 2025", "88021", "1st January 2025", "31st January 2025"),
        ("Omer Mazhar Rana", "", "Backend Developer", "January 2025", "February 2025", "150000", "1st January 2025", "31st January 2025"),
        ("Salman Ahmad", "", "Tech Fellow – AI Engineer", "January 2025", "February 2025", "40000", "1st January 2025", "31st January 2025"),
        ("Shujaan Azhar", "", "Tech Fellow – AI Engineer", "January 2025", "February 2025", "40000", "1st January 2025", "31st January 2025"),
        ("Tariq Asim", "Engineering", "Frontend Developer", "January 2025", "February 2025", "190000", "1st January 2025", "31st January 2025"),
        ("Wajdan Ahmed Khan", "", "Associate Program Manager", "January 2025", "February 2025", "101775", "1st January 2025", "31st January 2025"),

        # May 2025 Joiners
        ("Aqib Mehmood Satti", "", "", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Ayesha Tahir Awan", "", "", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Fahad Rao", "CEO & Directors / Product & Design Engineering / Product Team", "STANDARD CHARTERED - 038", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Farheen Foad", "Strategy & Fund Raising", "Meezan Bank - NAVALCOMPLEXE8", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Hataf Bin Atif", "", "UBL", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Iqra Zanib", "", "Bank Al-Habib", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Jahanzeb Ahmad", "", "Meezan Bank Limited", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Komal Babar", "Learning Engineering", "", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Mashhood Ali Rastgar", "CEO & Directors / Product & Design Engineering / Engineering team", "Meezan Bank - 089", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Muhammad Hammad Sarfraz", "Engineering", "", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Muhammad Hassan Dajana", "Strategy & Fund Raising", "FAYSAL BANK - 060", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Muhammad Jalal Khan", "", "Habib Metropolitan Bank Limited", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Muhammad Omer Mazhar Rana", "", "FAYSAL BANK, G-10", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Muhammad Raees Shujaan Azhar", "", "Askari Bank, Branch I-10 Markaz", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Muhammad Saad bin Idrees", "", "Soneri Bank Limited", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Muhammad Shoaib Khan", "", "Allied Bank Limited", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Muhammad Umar Raza", "Engineering", "Bank Alfalah", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Muhammad Zohaib Sheikh", "", "Bank Al habib", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Mujeeb ur Rehman", "", "STANDARD CHARTERED BANK - 038", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Salman Ahmad Khan", "", "Meezan Bank Limited", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Salwa Abdul Hayee", "", "Meezan Bank Limited", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Sheikh Nimra Rasheed", "", "HABIB BANK - 054", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Shiza Kamil", "Engineering", "Habib Bank Limited Sir Syed Road Karachi", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Sikandar Khurshid", "", "Allied Bank", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Syed Junaid Ali Zaidi", "", "ASKARI BANK LIMITED - 017", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Wajdan Ahmed Khan Yousafzai", "", "Bank Al-Falah Limited", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Zarmeena Siddique", "", "Meezan Bank Limited", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
        ("Zohaib Hassan Khan", "CEO & Directors / Operation Department", "FAYSAL BANK - 060", "May 2025", "June 2025", "", "1st May 2025", "31st May 2025"),
    ]

    # Build output rows
    output_rows = [
        [''],
        ['', 'List of Joiner and Leavers July 24 - June 25'],
        ['', 'Name', 'Department', 'Designation', 'Date of Joining', 'Date of Leaving', 'Salaries'],
    ]

    for entry in data_entries:
        name, dept, designation, join_month, leave_month, salary, join_date, leave_date = entry
        row = [
            '',
            name,
            dept,
            designation,
            join_date if join_month else '',  # joining date
            leave_date if leave_month else '',  # leaving date
            salary
        ]
        output_rows.append(row)

    # Create sheet
    print("Creating final OPL Joiners & Leavers sheet...")
    try:
        create_request = {
            'properties': {
                'title': 'OPL List of Joiners and Leavers 2024-2025'
            }
        }

        spreadsheet = service.spreadsheets().create(body=create_request).execute()
        new_sheet_id = spreadsheet['spreadsheetId']

        update_body = {'values': output_rows}
        service.spreadsheets().values().update(
            spreadsheetId=new_sheet_id,
            range='Sheet1!A1:G1000',
            valueInputOption='RAW',
            body=update_body
        ).execute()

        print(f"\nFINAL OPL SHEET CREATED!")
        print(f"URL: https://docs.google.com/spreadsheets/d/{new_sheet_id}")
        print(f"\nData Summary:")
        print(f"  Total Employees: {len(data_entries)}")
        print(f"  Format: Exact OWT match (List of Joiner and Leavers July 24 - June 25)")
        print(f"  Joining Dates: Filled with month-based estimates")
        print(f"  Leaving Dates: Filled with month-based estimates")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
