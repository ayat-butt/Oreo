"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { Button } from "@/components/ui/primitives";
import { apiGet } from "@/lib/client";

interface ContractOut {
  id: string;
  status: string;
  docs: { contract_id: string | null; nda_id: string | null; folder_url: string | null;
          contract_url: string | null; nda_url: string | null } | null;
  job: { status: string; error: string | null } | null;
}

const CHECKS = [
  "CNIC is correct",
  "Salary is correct",
  "Dates (joining / start / end) are correct",
  "HoD name & designation are correct",
  "Probation clause state is correct (removed for transitions; present for new hires)",
  "I have refreshed the preview after my last edit",
];

export default function PreviewPage({ params }: { params: { requestId: string } }) {
  const router = useRouter();
  const [data, setData] = useState<ContractOut | null>(null);
  const [tab, setTab] = useState<"contract" | "nda">("contract");
  const [refreshKey, setRefreshKey] = useState(0);
  const [checked, setChecked] = useState<boolean[]>(CHECKS.map(() => false));
  const [err, setErr] = useState("");

  const poll = useCallback(async () => {
    try {
      const d = await apiGet<ContractOut>(`/contracts/${params.requestId}`);
      setData(d);
      return d.job?.status;
    } catch (e) { setErr(String(e)); return "error"; }
  }, [params.requestId]);

  useEffect(() => {
    let alive = true;
    const tick = async () => {
      const s = await poll();
      if (alive && s !== "done" && s !== "error") setTimeout(tick, 2000);
    };
    tick();
    return () => { alive = false; };
  }, [poll]);

  const job = data?.job?.status;
  const docs = data?.docs;
  const allChecked = checked.every(Boolean);

  if (err) return <AppShell active="dashboard"><div className="text-danger">{err}</div></AppShell>;

  if (!data || job === "queued" || job === "running" || !docs?.contract_id) {
    const steps = ["Creating folder", "Filling contract", "Inserting JD", "Formatting", "Creating NDA"];
    return (
      <AppShell active="dashboard">
        <h1 className="font-serif text-2xl font-semibold text-slate-900">Generating contract…</h1>
        <p className="mt-1 text-sm text-slate-500">This takes around 30–60 seconds. You can stay on this page.</p>
        <div className="mt-6 max-w-md space-y-2">
          {steps.map((s, i) => (
            <div key={s} className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm">
              <span className="h-2 w-2 animate-pulse rounded-full bg-brand-green" style={{ animationDelay: `${i * 120}ms` }} />
              <span className="text-slate-600">{s}</span>
            </div>
          ))}
        </div>
        {job === "error" && <p className="mt-4 text-danger">Generation failed: {data?.job?.error}</p>}
      </AppShell>
    );
  }

  const docId = tab === "contract" ? docs.contract_id : docs.nda_id;
  const previewSrc = `https://docs.google.com/document/d/${docId}/preview?cb=${refreshKey}`;
  const editUrl = `https://docs.google.com/document/d/${docId}/edit`;

  return (
    <AppShell active="dashboard">
      <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-serif text-2xl font-semibold text-slate-900">Review the draft</h1>
          <p className="mt-1 text-sm text-slate-500">Edit directly in Google Docs; the sent PDF is always the latest version.</p>
        </div>
        <div className="flex gap-2">
          <a href={editUrl} target="_blank" rel="noreferrer">
            <Button variant="secondary">Open in Google Docs ↗</Button>
          </a>
          <Button variant="ghost" onClick={() => setRefreshKey((k) => k + 1)}>↻ Refresh preview</Button>
        </div>
      </div>

      {/* tabs */}
      <div className="mb-3 flex gap-1 border-b border-slate-200">
        <TabBtn active={tab === "contract"} onClick={() => setTab("contract")}>Contract</TabBtn>
        {docs.nda_id && <TabBtn active={tab === "nda"} onClick={() => setTab("nda")}>NDA</TabBtn>}
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <iframe
            key={previewSrc}
            title={`${tab} preview`}
            src={previewSrc}
            className="h-[70vh] w-full rounded-xl border border-slate-200 bg-white"
          />
        </div>

        {/* review gate */}
        <aside className="lg:col-span-1">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-card">
            <h2 className="font-serif text-lg font-semibold text-slate-900">Review checklist</h2>
            <p className="mt-1 text-sm text-slate-500">Confirm each item before continuing.</p>
            <div className="mt-4 space-y-2.5">
              {CHECKS.map((c, i) => (
                <label key={c} className="flex items-start gap-2.5 text-sm text-slate-700">
                  <input type="checkbox" className="mt-0.5 h-4 w-4" checked={checked[i]}
                         onChange={(e) => setChecked((p) => p.map((v, j) => (j === i ? e.target.checked : v)))} />
                  <span>{c}</span>
                </label>
              ))}
            </div>
            <Button className="mt-5 w-full" disabled={!allChecked}
                    onClick={() => router.push(`/draft/${params.requestId}/email`)}>
              Continue to email →
            </Button>
            {!allChecked && <p className="mt-2 text-center text-xs text-slate-400">Tick all items to continue</p>}
          </div>
        </aside>
      </div>
    </AppShell>
  );
}

function TabBtn({ active, children, onClick }: { active: boolean; children: React.ReactNode; onClick: () => void }) {
  return (
    <button onClick={onClick}
      className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium transition-colors ${
        active ? "border-brand-green text-brand-green-strong" : "border-transparent text-slate-500 hover:text-slate-700"
      }`}>
      {children}
    </button>
  );
}
