#!/usr/bin/env python3
"""Create Mohammed Raiyaan Junaid Hamid contract matching Muhammad Ahmed format."""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from hr_assistant.config import get_google_services

services = get_google_services()
docs_api = services["docs"]
drive = services["drive"]

# Create new document for Raiyaan
contract_title = "Mohammed Raiyaan Junaid Hamid - Contract"
doc = docs_api.documents().create(body={"title": contract_title}).execute()
doc_id = doc["documentId"]

# Contract content - exactly matching Muhammad Ahmed's format
contract_content = """Taleemabad

Plot 9, Times Square, Korang Road, I-10 – Markaz, Islamabad, Pakistan

Date: 16 April 2026	Private & Confidential

CNIC: 42301-556-7038-3

Name: Mohammed Raiyaan Junaid Hamid

Project-based Fellowship Contract

This contract for provision of project-based fellowship services for specific period of time ("Contract") is being entered into on this 3 June 2026 by and between:

Taleemabad (hereinafter referred to as the "Company", which expression shall, where the context permits, include its successors-in-interest, administrators, executors and permitted assigns) of the One Part;

AND

Mr. Mohammed Raiyaan Junaid Hamid bearing CNIC No: 42301-556-7038-3 (hereinafter referred to as "Fellow" and/or "You" and/or "Your" and/or "Yourself", which expression shall, where the context permits, include its successors-in-interest, authorized representatives and permitted assigns) of the Other Part;

Taleemabad and You may hereinafter, be individually referred to as "Party" and collectively as "Parties".

WHEREAS the Company is running a product management initiative;

AND WHEREAS You claim to be capable of hence, willing to provide the employment services for the said project to which Company agrees.

NOW, therefore for valuable consideration, the receipt and sufficiency of which are hereby acknowledged, the Parties hereby agree to the following:

Contract Period & Compensation

You agree to provide services for the duration of this Contract i.e., from 3rd June 2026 to 31st August 2026 ("Term") at the designation, department and salary mentioned herein below, among other terms and conditions of this Contract:

Designation: Product Management Intern
Department: Product
Monthly Compensation: PKR 40,000

(This is an all-inclusive package, and no other perks are available.)

Disbursement of the salary would be contingent upon the completion and acceptance of the deliverables, stated in the Job Description attached with this contract.

In-house Lunch will be provided, or an allowance in lieu.

The company will cover any travel incurred for business purposes.

Fellow is requested to bring his/her laptop for this period.

No travel or daily allowances will be furnished to the fellow, except for in-patient benefits insurance only for fellows and the travel allowance explicitly specified in the contract.

The fellow is entitled to annual leave of 3 working days for the course of the period accumulating on a monthly basis, and medical leave of 3 working days.

Medical Leaves can be availed for a maximum limit of 03 days it will be effective from the joining date, only for sickness or any other medical purposes.

Only unpaid leaves can be granted if the balance is exhausted.

Role Assignment

You are required to perform the duties included in but not limited to the Job Description, attached separately with this contract.

Performance & Evaluation

The fellow agrees to be held accountable for his performance, to be reviewed and quarterly evaluated for it by their line manager. If, in multiple max 2 quarter performance appraisals, the fellow's performance is consistently marked as sub-par, the Company reserves the right to terminate the fellow's contract.

Company Policy

During the Term, you will adhere to, and be subject to all relevant Company policies, rules and regulations, as may be in course from time to time. The terms of Your services shall include, inter alia, the following terms:

You will not be entitled to any other allowance and benefits except mention in this contract. This Contract shall not give You any right for permanent employment/absorption with the Company.

You will discharge all such deliverables, works, duties, responsibilities and authorities as assigned to You, efficiently and diligently to the satisfaction of the Company and You will not act in any manner contrary to the interest of the Company.

During the Term and after expiration/termination of the Contract, You will not disclose any information relating to the Company, its affiliates, business or customers and will not divulge any knowledge or trade secrets that You may obtain or come to know while serving the Company, unless compelled to do so by a court of law in which case You will formally intimate the Company in advance.

You will be bound to make good any loss or damage to the Company property caused by negligence, inadvertence, fraud, carelessness or any act or omission on Your part. The termination of Contract may not exonerate You from liability to make good any such loss or damage.

After completion of the Term, Taleemabad may, upon its sole discretion, renew/extend the Term of the Contract by signing a fresh contract.

Data Confidentiality

The fellow must adhere to all the terms and conditions stated and agreed upon in the Non-Disclosure Agreement signed separately from this contract upon confirmation.

Intellectual Property

The fellow must adhere to all the terms and conditions stated and agreed upon in the Non-Disclosure Agreement signed separately from this contract. All Intellectual Property rights subsisting or capable of subsisting in any work performed by You during the Term shall be and remain at all times, the absolute property of the Company.

Termination of This Contract

You agree that Taleemabad shall have the right to terminate this Contract, without assigning cause at its sole discretion, during the Term, subject to one month (30) day's prior notice or paying You the services fee in lieu thereof. No such notice is necessary after expiry of the Term.

The Company shall have the right to terminate this Contract at any time with immediate effect and without notice or any payment in lieu thereof, under the following instances:

If You commit any act or omission which is contrary to Company's interest.

If in the opinion of the Company, You at any point in time are under-performing or unsuited for the services being or to be rendered by You.

If You are found guilty of misconduct (including dishonesty, disorderly behavior, negligence, indiscipline, insubordination, disobedience of lawful requests or instructions) or conduct Yourself in a manner calculated to bring the Company into disrepute.

If You breach any of the terms and conditions of this Contract.

On expiry/termination of this Contract, You must forthwith return to the Company, in accordance with its instructions, all equipment, keys, passes, correspondence, records, specifications, software, discs, hardware, models, notes, reports and other documents including any copies thereof and any other property belonging to the Company or its associated companies/affiliates which is in Your possession or control. You will, if so required by the Company, confirm in writing that You have fully complied with Your obligations under this Sub-clause.

In case You or Taleemabad terminates this employment, the Company reserves the right to only remunerate You for the days worked.

In the event of termination, You will be held responsible for the timely hand over of any and all intellectual property, hardware, software, data, videos, assessments, games, images or any such output that they had either completed or were in the process of completing till the employment was active. If any of these items are either missing and/or damaged, You are responsible for replacing/repairing them. Taleemabad is entitled to legal action against You if this handover is not completed within 7 days of the termination of contract.

You agree not to undertake any form of paid work during the Term, even of a temporary nature, for any other party, except as directed by or with the written permission of the Company. The Company reserves the right to refuse such permission.

You undertake to disclose and report to Taleemabad any potential conflict of interest You may be aware of now or become aware later on. The conflict of interest covers, without limitation, situations that may influence or affect the conclusion of this Contract including agreeing or disagreeing to any term & condition thereof, the conduct and decision making of Taleemabad personnel having role in negotiating, concluding and ensuring compliance of this Contract, and any direct or indirect family or business relationship (whether current or of past i.e. within last two years) of You with any of Taleemabad personnel including Taleemabad affiliates. You undertake to immediately disclose and report to Taleemabad any situation leading to conflict of interest, and agrees that failing to this obligation will give right to Taleemabad (without prejudice to any other right(s) available to Taleemabad) for suspending, revoking and/or terminating this Contract.

This Contract constitutes the entire understanding between the Parties, and no waiver or modification thereof shall be valid unless in writing, signed by both Parties, and only to the extent specified therein.

If any provision of this Contract or any part of any provision is held to be invalid, or unenforceable, such provision or part (as the case may be) shall be ineffective only to the extent of such invalidity, or unenforceability, without rendering invalid, or unenforceable or otherwise prejudicing or affecting the remainder of such provision or any other provision of this Contract.

You agree to fully indemnify and hold harmless the Company, its directors, president, representatives, officers, agents, managers and fellows from any liabilities, causes of action, lawsuits, penalties, damages, claims or demands (including the costs and expenses and attorneys' reasonable fees on account thereof) that may be made by a third party for damages of any kind or nature (including, but not limited to, indirect, special, punitive, or exemplary damages for loss of business, loss of profits or business interruption) arising out of or in relation to Your actions, inactions or services under this Contract.

Failure by either Party to enforce any right given by or arising out of this Contract or under the governing law shall not operate as a waiver of such right.

This Contract is governed by and construed in accordance with the laws of the Islamic Republic of Pakistan and subject to the exclusive jurisdiction of the Islamabad Courts.

Sincerely,

For & On Behalf of

Haroon Yasin

CEO

_____________________________________

Date: _______________

OFFER ACCEPTANCE:

I, Mohammed Raiyaan Junaid Hamid, bearing CNIC # 42301-556-7038-3, agree and accept the terms and conditions of the contract with Taleemabad as set out in this agreement and will join Taleemabad on 3rd June 2026 (joining date).

Signature: _____________________________________

Date: _______________

Annexure A

Job Description: Product Management Intern

Key Responsibilities:

1. Support Product Discovery
   - Assist in conducting user interviews and surveys with students, parents, and teachers.
   - Perform competitive research to identify trends in EdTech and AI-enabled learning.
   - Help build low-fidelity wireframes or prototypes to test hypotheses.

2. Requirements & Documentation
   - Draft initial User Stories and assist in refining Product Requirement Documents (PRDs).
   - Document edge cases and "unhappy paths" to ensure a seamless user experience.
   - Help maintain the product backlog and ensure tickets are clearly defined for the Engineering team.

3. Data & Success Tracking
   - Monitor post-launch metrics and assist in preparing 30-day impact reports.
   - Gather data from product analytics tools to identify where users are getting stuck.
   - Draft internal Release Notes to keep stakeholders informed of new updates.

4. Agile Execution
   - Participate in daily stand-ups, sprint planning, and "Vibe Checks" (QA).
   - Coordinate between Design and Engineering to ensure assets are delivered on time.

Requirements

- Education: Currently pursuing or recently completed a degree in Computer Science (BSCS), Engineering, or a related technical field.
- Analytical Mindset: You love digging into "why" something is happening and back up your opinions with logic or data.
- Tech Savvy: A strong interest in AI/LLMs and how they can be used as "learning agents" for children.
- Communication: Excellent written and verbal communication skills (you'll be writing a lot of documentation!).
- Ownership: You don't wait to be told what to do; you see a gap and try to fill it.

Soft Skills

- Empathy: You can put yourself in the shoes of a 7-year-old student or a busy teacher.
- Curiosity: A hunger to learn the "Product Management" craft from senior mentors.
- Resilience: Comfortable with feedback and pivoting based on user evidence."""

# Insert the content
requests = [
    {
        "insertText": {
            "location": {"index": 1},
            "text": contract_content,
        }
    }
]
docs_api.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()

# Get the URL
file_meta = drive.files().get(fileId=doc_id, fields="id,name,webViewLink").execute()

print("=" * 100)
print("✅ CONTRACT UPDATED: Mohammed Raiyaan Junaid Hamid")
print("=" * 100)
print(f"\n📄 Google Docs Link:\n{file_meta['webViewLink']}\n")
print("Signing Authority: Haroon Yasin, CEO")
print("\nReady to proceed with NDA and email draft.")

