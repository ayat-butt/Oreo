#!/usr/bin/env python3
"""Recompute Total Allowance / Taxable / Total Deductions / Net for each month
and compare against stored + source values. Flags any mismatch."""
import json

with open('payroll/output/ayesha_ledger_data.json') as f:
    data = json.load(f)

def check(year, rows):
    print(f"\n===== {year} =====")
    tot = {k: 0 for k in ["gross","total_allowance","taxable","income_tax","eobi","unpaid_days","total_deductions","net"]}
    for r in rows:
        if r["gross"] is None:
            print(f"  {r['month']:<16} MISSING DATA (net ref {r['source_net']})")
            continue
        ta = r["gross"] + r["commute"] + r["pending"] + r["overtime"]
        tax = ta - r["medical"] - r["unpaid_days"]
        td = (r["income_tax"] + r["eobi"] + r["advance"] + r["abhi"]
              + r["loan"] + r["buscaro"] + r["lunch"] + r["unpaid_days"])
        net = ta - td
        bmo = r["basic"] + r["medical"] + r["other"]
        flags = []
        if ta != r["total_allowance"]: flags.append(f"TA calc {ta}!=stored {r['total_allowance']}")
        if abs(tax - r["taxable"]) > 1: flags.append(f"TAX calc {tax}!=stored {r['taxable']}")
        if abs(td - r["total_deductions"]) > 1: flags.append(f"TD calc {td}!=stored {r['total_deductions']}")
        if abs(net - r["net"]) > 1: flags.append(f"NET calc {net}!=stored {r['net']}")
        if bmo != r["gross"]: flags.append(f"Basic+Med+Other {bmo}!=Gross {r['gross']}")
        if r["net"] != r["source_net"]: flags.append(f"** stored net {r['net']} != SOURCE net {r['source_net']}")
        status = "OK" if not flags else "!! " + " | ".join(flags)
        print(f"  {r['month']:<16} Gross {r['gross']:>9,} TA {ta:>9,} Net {net:>9,}  {status}")
        for k in tot:
            tot[k] += r.get(k, 0) or 0
    print(f"  {'TOTAL':<16} Gross {tot['gross']:>9,} TA {tot['total_allowance']:>9,} "
          f"IT {tot['income_tax']:>8,} TD {tot['total_deductions']:>9,} Net {tot['net']:>10,}")
    return tot

check("2024", data["year_2024"])
check("2025", data["year_2025"])
