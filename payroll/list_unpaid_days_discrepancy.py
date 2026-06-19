#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
List all 20 employees with Unpaid Days discrepancy: Agent 5,720 vs Revised 0
"""

import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

with open('../token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

AGENT_PAYROLL_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'
REVISED_SHEET_ID = '1OUR1Bj9aqF1JekArcfqmlE3nP9kBHqMfJZWJuo3kK8E'

entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

print('=' * 140)
print('EMPLOYEES WITH UNPAID DAYS DISCREPANCY (Agent: 5,720 | Revised: 0)')
print('=' * 140)
print()

unpaid_days_employees = []

for entity in entities:
    # Load Agent data
    agent_result = service.spreadsheets().values().get(
        spreadsheetId=AGENT_PAYROLL_ID,
        range=f'{entity}!A1:AA500'
    ).execute()

    agent_values = agent_result.get('values', [])
    if not agent_values:
        continue

    agent_headers = agent_values[0]
    agent_col_map = {h.strip(): i for i, h in enumerate(agent_headers)}

    # Load Revised data
    revised_result = service.spreadsheets().values().get(
        spreadsheetId=REVISED_SHEET_ID,
        range=f'{entity}!A1:AA500'
    ).execute()

    revised_values = revised_result.get('values', [])
    if not revised_values:
        continue

    revised_headers = revised_values[0]
    revised_col_map = {h.strip(): i for i, h in enumerate(revised_headers)}

    # Build map of revised employees
    revised_data = {}
    for revised_row in revised_values[1:]:
        emp_name = revised_row[revised_col_map.get('Employee Name', 1)] if revised_col_map.get('Employee Name', 1) < len(revised_row) else ''
        if not emp_name:
            continue

        emp_name_lower = emp_name.lower()
        revised_unpaid = revised_row[revised_col_map.get('Unpaid Days', -1)] if revised_col_map.get('Unpaid Days', -1) >= 0 and revised_col_map.get('Unpaid Days', -1) < len(revised_row) else ''
        revised_data[emp_name_lower] = revised_unpaid

    # Check Agent data for discrepancy
    agent_unpaid_idx = agent_col_map.get('Unpaid Days', -1)
    agent_name_idx = agent_col_map.get('Employee Name', 1)
    job_title_idx = agent_col_map.get('Job Title', -1)
    department_idx = agent_col_map.get('Department', -1)
    gross_idx = agent_col_map.get('Gross Salary', -1)

    for agent_row in agent_values[1:]:
        emp_name = agent_row[agent_name_idx] if agent_name_idx < len(agent_row) else ''
        if not emp_name:
            continue

        emp_name_lower = emp_name.lower()

        if emp_name_lower not in revised_data:
            continue

        agent_unpaid = agent_row[agent_unpaid_idx] if agent_unpaid_idx >= 0 and agent_unpaid_idx < len(agent_row) else ''
        revised_unpaid = revised_data[emp_name_lower]

        agent_unpaid_str = str(agent_unpaid).strip()
        revised_unpaid_str = str(revised_unpaid).strip()

        # Check for discrepancy: Agent 5,720 vs Revised 0 (or blank)
        if agent_unpaid_str in ['5720', '5,720'] and revised_unpaid_str in ['', '0']:
            job_title = agent_row[job_title_idx] if job_title_idx >= 0 and job_title_idx < len(agent_row) else ''
            department = agent_row[department_idx] if department_idx >= 0 and department_idx < len(agent_row) else ''
            gross = agent_row[gross_idx] if gross_idx >= 0 and gross_idx < len(agent_row) else ''

            unpaid_days_employees.append({
                'name': emp_name,
                'entity': entity,
                'job_title': job_title,
                'department': department,
                'gross_salary': gross,
                'agent_unpaid': agent_unpaid,
                'revised_unpaid': revised_unpaid
            })

print(f'Total Employees Found: {len(unpaid_days_employees)}\n')
print()

print(f'{"#":<3} | {"Employee Name":<30} | {"Entity":<20} | {"Department":<25} | {"Gross Salary":>12}')
print('-' * 140)

for idx, emp in enumerate(unpaid_days_employees, 1):
    clean_name = emp['name'].encode('utf-8', errors='ignore').decode('utf-8')
    clean_dept = emp['department'].encode('utf-8', errors='ignore').decode('utf-8')
    print(f'{idx:<3} | {clean_name:<30} | {emp["entity"]:<20} | {clean_dept:<25} | {emp["gross_salary"]:>12}')

print()
print('=' * 140)
print('DETAILS')
print('=' * 140)
print()

for idx, emp in enumerate(unpaid_days_employees, 1):
    clean_name = emp['name'].encode('utf-8', errors='ignore').decode('utf-8')
    clean_dept = emp['department'].encode('utf-8', errors='ignore').decode('utf-8')
    print(f'{idx}. {clean_name}')
    print(f'   Entity: {emp["entity"]}')
    print(f'   Job Title: {emp["job_title"]}')
    print(f'   Department: {clean_dept}')
    print(f'   Gross Salary: {emp["gross_salary"]}')
    print(f'   Agent Unpaid Days: {emp["agent_unpaid"]}')
    print(f'   Revised Unpaid Days: {emp["revised_unpaid"] if emp["revised_unpaid"] else "(blank)"}')
    print()

print()
print('=' * 140)
print('ANALYSIS')
print('=' * 140)
print()
print('Pattern: All 20 employees show 5,720 unpaid days in Agent but 0/blank in Revised')
print('Possible reasons:')
print('  1. 5,720 PKR might be lunch meal deduction misplaced in Unpaid Days column')
print('  2. These might be NIETE ICT employees with standard meal deduction')
print('  3. Agent payroll incorrectly populated Unpaid Days instead of using 0')
print()
