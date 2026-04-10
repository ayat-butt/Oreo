# Project Background

## What This Agent Does
An HR assistant that automates the most time-consuming HR inbox tasks:
- Reading and labelling incoming emails by topic (Contracts / Benefits / Payroll / Queries)
- Drafting professional replies for review
- Creating calendar invites from email content
- Generating HR documents (offer letters, contracts, onboarding)
- Sending notifications to Microsoft Teams channels

## Why We Built This
Following the AI Agent Primer (Taleemabad, January 2026), the goal is to build
an agent that learns over time. It starts as an intern — smart but inexperienced.
With every session and every correction saved to memory.md, it becomes more capable.

## Integrations
1. Gmail            — primary email inbox
2. Google Calendar  — scheduling and invites
3. Microsoft Teams  — team notifications and meetings
4. Claude (claude-opus-4-6) — AI brain for categorisation, drafting, generating

## The Loop (from the Primer)
Task → Read memory → Produce output → Save learnings back to memory → Next session

## Key Principle
Never send or create anything without showing a preview first.
The human is always in the loop for final approval.
