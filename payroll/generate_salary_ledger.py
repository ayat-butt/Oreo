#!/usr/bin/env python3
"""
Generate a Salary Ledger PDF matching the Taleemabad/Orenda template.
HTML -> PDF via headless Microsoft Edge (Chromium). Read-only on data.

Usage:
    python payroll/generate_salary_ledger.py 2024
    python payroll/generate_salary_ledger.py 2025
"""
import json
import sys
import os
import subprocess
from datetime import date

DATA_FILE = "payroll/output/ayesha_ledger_data.json"
OUT_DIR = "payroll/output"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# ---- palette (sampled from the reference ledger) ----
NAVY = "#1d2d54"
TEAL = "#2ba2b4"
GREEN_BG = "#e6f4ea"
GREEN_HEAD = "#3f9d6d"
PINK_BG = "#fce7e9"
PINK_HEAD = "#d9636b"
GREY_BOX = "#f4f6f9"
BORDER = "#d7dde6"

# columns: (key, line1, line2, group)  group in {plain, add, ded, bold}
COLUMNS = [
    ("gross",          "Gross",   "Salary",     "plain"),
    ("basic",          "Basic",   "Salary",     "plain"),
    ("medical",        "Medical", "Allow.",     "plain"),
    ("other",          "Other",   "Allow.",     "plain"),
    ("commute",        "Commute", "Allow.",     "add"),
    ("pending",        "Pending", "Dues",       "add"),
    ("overtime",       "Overtime","",           "add"),
    ("total_allowance","Total",   "Allowance",  "bold"),
    ("taxable",        "Taxable", "Salary",     "bold"),
    ("income_tax",     "Income",  "Tax",        "ded"),
    ("eobi",           "EOBI",    "",           "ded"),
    ("advance",        "Advance", "",           "ded"),
    ("abhi",           "Abhi",    "",           "ded"),
    ("loan",           "Loan",    "",           "ded"),
    ("buscaro",        "BusCaro", "",           "ded"),
    ("lunch",          "Lunch",   "Meal",       "ded"),
    ("unpaid_days",    "Unpaid",  "Days",       "ded"),
    ("total_deductions","Total",  "Deductions", "bold"),
    ("net",            "Net",     "Salary",     "bold"),
]


def fmt(v):
    if v is None:
        return "—"
    if isinstance(v, (int, float)):
        if round(v) == 0:
            return "—"
        return f"{round(v):,}"
    return str(v)


def cell_class(group, val):
    cls = {"plain": "c", "add": "c add", "ded": "c ded", "bold": "c bold"}[group]
    return cls


def build_row(rec, missing=False):
    tds = [f'<td class="month"><span>{rec["month"].split()[0]}</span>'
           f'<span class="yr">{rec["month"].split()[1]}</span></td>']
    for key, _, _, group in COLUMNS:
        v = rec.get(key)
        tds.append(f'<td class="{cell_class(group, v)}">{fmt(v)}</td>')
    cls = ' class="missing"' if missing else ""
    return f"<tr{cls}>" + "".join(tds) + "</tr>"


def build_total_row(rows):
    sums = {}
    for key, _, _, _ in COLUMNS:
        sums[key] = sum((r.get(key) or 0) for r in rows if r.get("gross") is not None)
    tds = ['<td class="month total-lbl">TOTAL</td>']
    for key, _, _, group in COLUMNS:
        tds.append(f'<td class="c total-c">{fmt(sums[key])}</td>')
    return "<tr class='totalrow'>" + "".join(tds) + "</tr>"


def header_cells():
    out = ['<th class="month-h">Month</th>']
    for key, l1, l2, group in COLUMNS:
        gcls = {"plain": "", "add": " hadd", "ded": " hded", "bold": " hbold"}[group]
        l2html = f"<br>{l2}" if l2 else ""
        out.append(f'<th class="h{gcls}">{l1}{l2html}</th>')
    return "".join(out)


def orenda_logo():
    # CSS recreation of the Orenda wordmark (teal pin + lowercase serif word)
    return (
        '<div class="orenda">'
        '<svg width="26" height="26" viewBox="0 0 24 24" fill="none">'
        '<circle cx="12" cy="8" r="5.2" stroke="#c0563b" stroke-width="2.1"/>'
        '<line x1="12" y1="13" x2="12" y2="22" stroke="#1d2d54" stroke-width="2.1"/>'
        '</svg>'
        '<span>orenda</span></div>'
    )


def taleemabad_logo():
    return ('<div class="tab"><span class="t1">taleem</span>'
            '<span class="t2">abad</span></div>')


def build_html(year, meta, rows):
    generated = date.today().strftime("%d %B %Y")
    eid = meta["employee_id"]
    css = f"""
    @page {{ size: A4 landscape; margin: 12mm 10mm; }}
    * {{ box-sizing: border-box; }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; color:{NAVY}; margin:0; font-size:9px; }}
    .head {{ display:flex; align-items:center; justify-content:space-between; padding-bottom:8px; }}
    .orenda {{ display:flex; flex-direction:column; align-items:center; }}
    .orenda svg {{ margin-bottom:-2px; }}
    .orenda span {{ font-family:Georgia,serif; font-size:20px; letter-spacing:4px; color:#3a3a3a; }}
    .title {{ text-align:center; }}
    .title h1 {{ margin:0; font-size:26px; letter-spacing:3px; color:{NAVY}; font-weight:800; }}
    .title .sub {{ margin-top:3px; color:{TEAL}; font-size:10px; letter-spacing:1px; }}
    .tab {{ font-weight:800; font-size:22px; line-height:0.95; text-align:center; }}
    .tab .t1 {{ color:{TEAL}; }} .tab .t2 {{ color:{NAVY}; display:block; }}
    .rule {{ height:3px; background:{NAVY}; border-radius:2px; margin-bottom:10px; }}
    .info {{ background:{GREY_BOX}; border:1px solid {BORDER}; border-radius:8px;
             display:flex; justify-content:space-between; padding:12px 18px; margin-bottom:9px; }}
    .info .col {{ display:flex; flex-direction:column; gap:7px; }}
    .info .lbl {{ color:{TEAL}; font-size:8px; letter-spacing:1.5px; font-weight:700; }}
    .info .val {{ color:{NAVY}; font-size:13px; font-weight:700; margin-top:1px; }}
    .info .pair {{ display:flex; gap:30px; }}
    .info .gen {{ color:#8a93a3; font-size:8.5px; align-self:flex-end; }}
    .legend {{ display:flex; gap:10px; margin-bottom:8px; }}
    .lg {{ font-size:8.5px; padding:5px 10px; border-radius:6px; font-weight:600; }}
    .lg.g {{ background:{GREEN_BG}; color:{GREEN_HEAD}; }}
    .lg.r {{ background:{PINK_BG}; color:{PINK_HEAD}; }}
    .lg .sw {{ display:inline-block; width:9px; height:9px; border-radius:2px; margin-right:5px; vertical-align:middle; }}
    .lg.g .sw {{ background:{GREEN_HEAD}; }} .lg.r .sw {{ background:{PINK_HEAD}; }}
    table {{ width:100%; border-collapse:collapse; table-layout:fixed; }}
    th, td {{ border:1px solid {BORDER}; padding:4px 4px; text-align:right; font-size:8px; }}
    thead th {{ background:{NAVY}; color:#fff; font-weight:700; text-align:right; font-size:7.6px;
                line-height:1.1; vertical-align:bottom; }}
    th.month-h, td.month {{ text-align:left; }}
    th.month-h {{ background:{NAVY}; color:#fff; }}
    td.month {{ font-weight:800; color:{NAVY}; line-height:1.05; }}
    td.month span {{ display:block; }}
    td.month .yr {{ font-weight:500; font-size:7.5px; color:#6b7280; }}
    .h.hbold {{ background:#16223f; }}
    td.add {{ background:{GREEN_BG}; }}
    td.ded {{ background:{PINK_BG}; }}
    td.bold {{ font-weight:800; color:{NAVY}; }}
    tr.totalrow td {{ background:{NAVY}; color:#fff; font-weight:800; border-color:{NAVY}; }}
    tr.totalrow td.total-lbl {{ text-align:left; }}
    tr:nth-child(even) td.c:not(.add):not(.ded) {{ background:#fbfcfd; }}
    .foot {{ display:flex; justify-content:space-between; margin-top:14px; gap:30px; }}
    .formula {{ flex:1; }}
    .formula h3 {{ color:{TEAL}; font-size:9px; letter-spacing:1.5px; margin:0 0 6px; }}
    .formula .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:3px 24px; font-size:8px; }}
    .formula b {{ color:{NAVY}; }}
    .formula .eq {{ color:#55607a; }}
    .sign {{ width:230px; text-align:left; border-left:2px solid {TEAL}; padding-left:16px; }}
    .sign .sig {{ font-family:'Segoe Script','Brush Script MT',cursive; font-size:22px; color:{NAVY}; height:30px; }}
    .sign .nm {{ font-weight:800; color:{NAVY}; font-size:11px; }}
    .sign .ti {{ color:{TEAL}; font-weight:700; font-size:9px; }}
    .sign .ct {{ color:#55607a; font-size:8.5px; margin-top:2px; }}
    .pgfoot {{ position:fixed; bottom:-6mm; left:0; right:0; background:{NAVY}; color:#fff;
               text-align:center; font-size:8px; padding:6px; }}
    """
    rows_html = "".join(build_row(r, missing=(r.get("gross") is None)) for r in rows)
    total_html = build_total_row(rows)

    formulas = [
        ("Basic Salary:", "= Gross Salary × 90%"),
        ("Medical Allow.:", "= Basic Salary × 10%"),
        ("Other Allow.:", "= Gross – Basic – Medical"),
        ("Total Allowance:", "= Basic + Medical + Other + Commute + Pending + Overtime"),
        ("Taxable Salary:", "= Total Allowance – Medical – Unpaid Days"),
        ("Total Deductions:", "= IT + EOBI + Advance + Abhi + Loan + BusCaro + Lunch + Unpaid Days"),
        ("Net Salary:", "= Total Allowance – Total Deductions"),
    ]
    fhtml = "".join(
        f'<div><b>{lbl}</b> <span class="eq">{eq}</span></div>' for lbl, eq in formulas
    )

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head><body>
    <div class="head">
      {orenda_logo()}
      <div class="title"><h1>SALARY LEDGER</h1>
        <div class="sub">{meta['subtitle']}</div></div>
      {taleemabad_logo()}
    </div>
    <div class="rule"></div>
    <div class="info">
      <div class="col">
        <div><div class="lbl">EMPLOYEE NAME</div><div class="val">{meta['name']}</div></div>
        <div><div class="lbl">EMPLOYEE ID</div><div class="val">{eid}</div></div>
      </div>
      <div class="col">
        <div><div class="lbl">CNIC</div><div class="val">{meta['cnic']}</div></div>
        <div><div class="lbl">JOINING DATE</div><div class="val">{meta['joining']}</div></div>
      </div>
      <div class="gen">Generated: {generated}</div>
    </div>
    <div class="legend">
      <div class="lg g"><span class="sw"></span>Addition (Commute Allow., Pending Dues, Overtime)</div>
      <div class="lg r"><span class="sw"></span>Deduction (Income Tax, EOBI, Advance, Abhi, Loan, BusCaro, Lunch, Unpaid Days)</div>
    </div>
    <table>
      <thead><tr>{header_cells()}</tr></thead>
      <tbody>{rows_html}{total_html}</tbody>
    </table>
    <div class="foot">
      <div class="formula"><h3>FORMULA REFERENCE</h3><div class="grid">{fhtml}</div></div>
      <div class="sign">
        <div class="sig">Zeshan</div>
        <div class="nm">Zeshan Ali Dhillon</div>
        <div class="ti">Head of People &amp; Culture</div>
        <div class="ct">zeshan.dhillon@taleemabad.com<br>+92-331-9754569</div>
      </div>
    </div>
    <div class="pgfoot">This is a system-generated salary ledger.&nbsp;&nbsp;For queries contact hr@taleemabad.com</div>
    </body></html>"""


def main():
    year = sys.argv[1] if len(sys.argv) > 1 else "2024"
    with open(DATA_FILE) as f:
        data = json.load(f)
    emp = data["employee"]

    if year == "2024":
        rows = data["year_2024"]
        meta = {"subtitle": "Confidential · Calendar Year 2024 · May – December 2024",
                "employee_id": emp["employee_id_2024"]}
    else:
        rows = data["year_2025"]
        meta = {"subtitle": "Confidential · Calendar Year 2025 · January – December 2025",
                "employee_id": emp["employee_id_2025"]}
    meta.update({"name": emp["name"], "cnic": emp["cnic"], "joining": "01 May 2024"})

    html = build_html(year, meta, rows)
    os.makedirs(OUT_DIR, exist_ok=True)
    html_path = os.path.abspath(os.path.join(OUT_DIR, f"Ayesha_Jamshaid_Salary_Ledger_{year}.html"))
    pdf_path = os.path.abspath(os.path.join(OUT_DIR, f"Ayesha_Jamshaid_Salary_Ledger_{year}.pdf"))
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML written: {html_path}")

    subprocess.run([EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}", f"file:///{html_path.replace(os.sep, '/')}"],
                   check=True, timeout=90)
    print(f"PDF written:  {pdf_path}")


if __name__ == "__main__":
    main()
