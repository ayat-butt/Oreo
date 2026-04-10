@echo off
:: Lunar — Daily Probation Tracker Agent
:: Triggered by Windows Task Scheduler at 9:30 AM PKT every day.

cd /d "C:\Agent Oreo"
python lunar_agent.py >> logs\lunar_scheduler.log 2>&1
