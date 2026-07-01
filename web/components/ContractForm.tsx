"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Building2, User, Wallet, Stamp, FileText, ArrowLeft, ArrowRight } from "lucide-react";
import { Section, Field, Button, Toggle, inputClass } from "@/components/ui/primitives";
import { apiPost } from "@/lib/client";
import { toDisplayDate, maskCnic } from "@/lib/format";
import { ENTITIES, PAIRS, TYPE_LABELS, ccDomainOk } from "@/lib/matrix";

export interface FormDetail {
  prefill: Record<string, string | null>;
  missing_fields: string[];
  hints: Record<string, string | null>;
}

type Form = {
  name: string; cnic: string; email: string; designation: string; department: string;
  entity: string; employment_type: string; gender: string;
  salary: string; joining_date: string; start_date: string; end_date: string;
  duration: string; prev_contract_date: string;
  hod_name: string; hod_designation: string; jd_doc_id: string; jd_text: string;
  direct_report: string; indirect_report: string;
  is_transition: boolean; cc_list: string;
};

const EMPTY: Form = {
  name: "", cnic: "", email: "", designation: "", department: "",
  entity: "", employment_type: "", gender: "",
  salary: "", joining_date: "", start_date: "", end_date: "",
  duration: "", prev_contract_date: "", hod_name: "", hod_designation: "",
  jd_doc_id: "", jd_text: "", direct_report: "", indirect_report: "",
  is_transition: false, cc_list: "",
};

export function ContractForm({
  detail,
  sourceLabel,
  back,
  sourceNote,
  meta,
}: {
  detail: FormDetail;
  sourceLabel: "Markaz" | "Email";
  back: { href: string; label: string };
  sourceNote: string;
  meta: { markaz_application_id?: number; email_candidate_id?: string; idempotencyKey: string };
}) {
  const router = useRouter();
  const p = detail.prefill;
  const [f, setF] = useState<Form>(() => ({
    ...EMPTY,
    name: p.name ?? "",
    cnic: p.cnic ?? "",
    email: p.email ?? "",
    designation: p.designation ?? "",
    department: p.department ?? "",
    employment_type: p.employment_type ?? "full_time",
    jd_text: p.jd_text ?? "",
    salary: p.salary ?? "",
    joining_date: p.joining_date ?? "",
    hod_name: p.hod_name ?? "",
  }));
  const [submitErr, setSubmitErr] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const set = (k: keyof Form, v: string | boolean) => setF((prev) => ({ ...prev, [k]: v }));
  const isProject = f.employment_type === "project" || f.employment_type === "part_time";
  const isAddendum = f.employment_type === "addendum";
  const src = (field: string): "Markaz" | "Email" | "Manual" => (p[field] ? sourceLabel : "Manual");

  const badCc = f.cc_list.split(",").map((s) => s.trim()).filter(Boolean).filter((e) => !ccDomainOk(e));

  function validate(): string | null {
    const req: [string, string][] = [
      ["name", f.name], ["cnic", f.cnic], ["designation", f.designation],
      ["department", f.department], ["salary", f.salary], ["joining_date", f.joining_date],
    ];
    if (!f.entity) return "Please select the contract entity (OPL / OWT, or Taleemabad for senior leadership).";
    if (!f.employment_type) return "Please select the employment type.";
    for (const [k, v] of req) if (!v) return `Missing required field: ${k}`;
    if (!f.gender) return "Please select gender — it sets the Mr./Miss salutation in the contract.";
    if (isProject && (!f.start_date || !f.end_date || !f.duration))
      return "Project/part-time needs start date, end date and duration.";
    if (isAddendum && (!f.prev_contract_date || !f.end_date))
      return "Addendum needs the previous contract date and the extension end date.";
    if (badCc.length) return `CC not allowed (must be Taleemabad/NIETE): ${badCc.join(", ")}`;
    return null;
  }

  async function onGenerate() {
    setSubmitErr("");
    const v = validate();
    if (v) { setSubmitErr(v); return; }
    setSubmitting(true);
    const emp: Record<string, unknown> = {
      name: f.name, cnic: f.cnic, designation: f.designation, department: f.department,
      salary: f.salary, joining_date: toDisplayDate(f.joining_date),
      entity: f.entity, employment_type: f.employment_type,
      gender: f.gender || null, is_transition: f.is_transition,
      hod_name: f.hod_name || null, hod_designation: f.hod_designation || null,
      direct_report: f.direct_report || null, indirect_report: f.indirect_report || null,
      jd_doc_id: f.jd_doc_id || null, jd_text: f.jd_text || null, email: f.email || null,
      cc_list: f.cc_list ? f.cc_list.split(",").map((s) => s.trim()).filter(Boolean) : null,
    };
    if (isProject) {
      emp.start_date = toDisplayDate(f.start_date);
      emp.end_date = toDisplayDate(f.end_date);
      emp.duration = f.duration;
    }
    if (isAddendum) {
      emp.prev_contract_date = toDisplayDate(f.prev_contract_date);
      emp.end_date = toDisplayDate(f.end_date);
    }

    try {
      const res = await apiPost<{ request_id: string }>("/contracts", {
        emp,
        ...(meta.markaz_application_id != null ? { markaz_application_id: meta.markaz_application_id } : {}),
        ...(meta.email_candidate_id ? { email_candidate_id: meta.email_candidate_id } : {}),
        idempotency_key: meta.idempotencyKey,
      });
      router.push(`/draft/${res.request_id}/preview`);
    } catch (e) {
      setSubmitErr(String(e));
      setSubmitting(false);
    }
  }

  return (
    <>
      <div className="mb-5">
        <Link href={back.href} className="inline-flex items-center gap-1 text-sm text-slate-500 transition-colors hover:text-slate-700"><ArrowLeft size={14} /> {back.label}</Link>
        <h1 className="mt-1 font-serif text-2xl font-semibold text-slate-900">Draft contract</h1>
        <p className="mt-1 text-sm text-slate-500">{f.name || "Candidate"} · {sourceNote}</p>
      </div>

      <div className="space-y-5">
        <Section title="Entity & contract type" subtitle="Selects which template + NDA are generated." icon={Building2}>
          <Field label="Entity" required
                 hint="Use OPL or OWT (Orenda) for everyone. Taleemabad Inc is for senior leadership only.">
            <select className={inputClass} value={f.entity} onChange={(e) => set("entity", e.target.value)}>
              <option value="">— Select entity —</option>
              {ENTITIES.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </Field>
          <Field label="Employment type" required source={src("employment_type")}>
            <select className={inputClass} value={f.employment_type} disabled={!f.entity}
                    onChange={(e) => set("employment_type", e.target.value)}>
              {!f.entity && <option value="">— choose entity first —</option>}
              {(PAIRS[f.entity] ?? []).map((t) => <option key={t} value={t}>{TYPE_LABELS[t]}</option>)}
            </select>
          </Field>
        </Section>

        <Section title="Personal" icon={User}>
          <Field label="Full legal name" required source={src("name")}>
            <input className={inputClass} value={f.name} onChange={(e) => set("name", e.target.value)} />
          </Field>
          <Field label="Gender (salutation)" required hint="Sets Mr./Miss in the contract." source="Manual">
            <select className={inputClass} value={f.gender} onChange={(e) => set("gender", e.target.value)}>
              <option value="">— select —</option>
              <option value="male">Male (Mr.)</option>
              <option value="female">Female (Miss)</option>
            </select>
          </Field>
          <Field label="CNIC" required source={src("cnic")} hint={f.cnic ? `Stored: ${maskCnic(f.cnic)}` : "13 digits, e.g. 61101-1234567-8"}>
            <input className={`${inputClass} tnum`} value={f.cnic} onChange={(e) => set("cnic", e.target.value)} placeholder="#####-#######-#" />
          </Field>
          <Field label="Candidate email (To)" source={src("email")} hint="Personal email allowed.">
            <input className={inputClass} value={f.email} onChange={(e) => set("email", e.target.value)} />
          </Field>
        </Section>

        <Section title="Compensation & dates" icon={Wallet}>
          <Field label="Gross monthly salary (PKR)" required source={src("salary")}>
            <input className={`${inputClass} tnum`} value={f.salary} onChange={(e) => set("salary", e.target.value)} placeholder="100,000" />
          </Field>
          <Field label="Joining / effective date" required source={src("joining_date")}>
            <input type="date" className={`${inputClass} tnum`} value={f.joining_date} onChange={(e) => set("joining_date", e.target.value)} />
          </Field>
          {isProject && (
            <>
              <Field label="Start date" required source="Manual">
                <input type="date" className={`${inputClass} tnum`} value={f.start_date} onChange={(e) => set("start_date", e.target.value)} />
              </Field>
              <Field label="End date" required source="Manual">
                <input type="date" className={`${inputClass} tnum`} value={f.end_date} onChange={(e) => set("end_date", e.target.value)} />
              </Field>
              <Field label="Duration (months)" required source="Manual">
                <input className={`${inputClass} tnum`} value={f.duration} onChange={(e) => set("duration", e.target.value)} placeholder="3" />
              </Field>
            </>
          )}
          {isAddendum && (
            <>
              <Field label="Previous contract date" required source="Manual"
                     hint="The date of the contract being extended.">
                <input type="date" className={`${inputClass} tnum`} value={f.prev_contract_date} onChange={(e) => set("prev_contract_date", e.target.value)} />
              </Field>
              <Field label="Extension end date (till)" required source="Manual"
                     hint="The extension runs from the joining/effective date above until this date.">
                <input type="date" className={`${inputClass} tnum`} value={f.end_date} onChange={(e) => set("end_date", e.target.value)} />
              </Field>
            </>
          )}
          <Field label="Designation" required source={src("designation")}>
            <input className={inputClass} value={f.designation} onChange={(e) => set("designation", e.target.value)} />
          </Field>
          <Field label="Department" required source={src("department")}>
            <input className={inputClass} value={f.department} onChange={(e) => set("department", e.target.value)} />
          </Field>
        </Section>

        <Section title="Head of Department (signing block)" subtitle="Signing date is set to today automatically." icon={Stamp}>
          <Field label="HoD name" source={src("hod_name")}
                 hint={p.hod_name ? "From “reporting to …” in the email — confirm it's the signing HoD." : undefined}>
            <input className={inputClass} value={f.hod_name} onChange={(e) => set("hod_name", e.target.value)} />
          </Field>
          <Field label="HoD designation" source="Manual">
            <input className={inputClass} value={f.hod_designation} onChange={(e) => set("hod_designation", e.target.value)} />
          </Field>
          {isProject && (
            <Field label="Direct Report to (line manager)" source="Manual"
                   hint="Project contracts only — appears in the Offer Acceptance section.">
              <input className={inputClass} value={f.direct_report} onChange={(e) => set("direct_report", e.target.value)} />
            </Field>
          )}
        </Section>

        <Section title="Job description & clauses" icon={FileText}>
          <Field label="Job description (Annexure-A)" full source={src("jd_text")}
                 hint="One item per line; a short line ending with ':' becomes a bold sub-heading, others become bullets.">
            <textarea className={`${inputClass} min-h-[180px] font-sans`} value={f.jd_text}
                      onChange={(e) => set("jd_text", e.target.value)}
                      placeholder={"(No JD found — paste it here)\nKey Responsibilities:\n• Lead the program team and set quarterly goals\n• Manage partner relationships"} />
          </Field>
          <div className="sm:col-span-2">
            <Toggle checked={f.is_transition} onChange={(v) => set("is_transition", v)}>
              <span className="font-medium text-slate-800">Internal transition (existing employee)</span>
              <span className="mt-0.5 block text-warning">⚠ Turning this on removes the probation clause from the contract.</span>
            </Toggle>
          </div>
          <Field label="Welcome-email CC (comma-separated)" full source="Manual"
                 hint="Must be @taleemabad.com / @niete.edu.pk / @niete.pk."
                 error={badCc.length ? `Not allowed: ${badCc.join(", ")}` : undefined}>
            <input className={inputClass} value={f.cc_list} onChange={(e) => set("cc_list", e.target.value)} placeholder="hiring@taleemabad.com, hr@taleemabad.com" />
          </Field>
        </Section>

        {submitErr && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-danger" role="alert">{submitErr}</div>
        )}

        <div className="sticky bottom-0 flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white/90 px-4 py-3 shadow-pop backdrop-blur">
          <span className="text-sm text-slate-500">
            {f.entity && f.employment_type ? (
              <>Template: <b className="text-slate-700">{ENTITIES.find((e) => e.value === f.entity)?.label} · {TYPE_LABELS[f.employment_type]}</b></>
            ) : (
              <span className="text-slate-400">Select an entity &amp; type to generate</span>
            )}
          </span>
          <Button onClick={onGenerate} disabled={submitting}>
            {submitting ? "Generating…" : <>Generate draft <ArrowRight size={16} /></>}
          </Button>
        </div>
      </div>
    </>
  );
}
