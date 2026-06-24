"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { ExternalLink, RefreshCw, FileText, ShieldCheck, Check, ArrowRight, Loader2, AlertTriangle } from "lucide-react";
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
  const doneCount = checked.filter(Boolean).length;
  const allChecked = doneCount === CHECKS.length;

  if (err) return <AppShell active="dashboard"><div className="flex items-center gap-2 rounded-2xl border border-red-200 bg-danger-soft p-5 text-danger"><AlertTriangle size={18} />{err}</div></AppShell>;

  if (!data || job === "queued" || job === "running" || !docs?.contract_id) {
    const steps = ["Creating folder", "Filling contract", "Inserting job description", "Applying formatting", "Creating NDA"];
    return (
      <AppShell active="dashboard">
        <div className="mx-auto max-w-md rounded-2xl border border-hairline bg-white p-8">
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-green-soft text-brand-green-strong">
              <Loader2 size={22} className="animate-spin" />
            </span>
            <div>
              <h1 className="text-xl font-semibold text-ink">Generating contract…</h1>
              <p className="text-sm text-mute">Around 30–60 seconds — you can stay here.</p>
            </div>
          </div>
          <div className="mt-6 space-y-2">
            {steps.map((s, i) => (
              <div key={s} className="flex items-center gap-3 rounded-xl bg-cream-card px-4 py-2.5 text-sm">
                <span className="h-2 w-2 animate-pulse rounded-full bg-brand-green" style={{ animationDelay: `${i * 150}ms` }} />
                <span className="text-body">{s}</span>
              </div>
            ))}
          </div>
          {job === "error" && (
            <p className="mt-4 flex items-center gap-2 text-sm text-danger"><AlertTriangle size={16} /> Generation failed: {data?.job?.error}</p>
          )}
        </div>
      </AppShell>
    );
  }

  const docId = tab === "contract" ? docs.contract_id : docs.nda_id;
  const previewSrc = `https://docs.google.com/document/d/${docId}/preview?cb=${refreshKey}`;
  const editUrl = `https://docs.google.com/document/d/${docId}/edit`;

  return (
    <AppShell active="dashboard">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-ink">Review the draft</h1>
          <p className="mt-1 text-sm text-mute">Edit directly in Google Docs; the sent PDF is always the latest version.</p>
        </div>
        <div className="flex gap-2">
          <a href={editUrl} target="_blank" rel="noreferrer">
            <Button variant="secondary"><ExternalLink size={15} /> Open in Google Docs</Button>
          </a>
          <Button variant="ghost" onClick={() => setRefreshKey((k) => k + 1)}><RefreshCw size={15} /> Refresh</Button>
        </div>
      </div>

      {/* tabs */}
      <div className="mb-4 flex gap-1 border-b border-hairline">
        <TabBtn active={tab === "contract"} onClick={() => setTab("contract")} icon={FileText}>Contract</TabBtn>
        {docs.nda_id && <TabBtn active={tab === "nda"} onClick={() => setTab("nda")} icon={ShieldCheck}>NDA</TabBtn>}
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <iframe
            key={previewSrc}
            title={`${tab} preview`}
            src={previewSrc}
            className="h-[72vh] w-full rounded-2xl border border-hairline bg-white shadow-md"
          />
        </div>

        {/* review gate */}
        <aside className="lg:col-span-1">
          <div className="sticky top-6 rounded-2xl border border-hairline bg-white p-5">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-ink">Review checklist</h2>
              <span className="rounded-full bg-cream-deep px-2 py-0.5 text-xs font-medium tabular-nums text-mute">{doneCount}/{CHECKS.length}</span>
            </div>
            <p className="mt-1 text-sm text-mute">Confirm each item before continuing.</p>
            <div className="mt-4 space-y-1.5">
              {CHECKS.map((c, i) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => setChecked((p) => p.map((v, j) => (j === i ? !v : v)))}
                  className="flex w-full items-start gap-2.5 rounded-xl px-2 py-2 text-left text-sm transition-colors hover:bg-cream-card"
                >
                  <span className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md border transition-colors ${checked[i] ? "border-brand-green bg-brand-green text-white" : "border-stone bg-white text-transparent"}`}>
                    <Check size={13} strokeWidth={3} />
                  </span>
                  <span className={checked[i] ? "text-mute line-through" : "text-body"}>{c}</span>
                </button>
              ))}
            </div>
            <Button className="mt-5 w-full" disabled={!allChecked} onClick={() => router.push(`/draft/${params.requestId}/email`)}>
              Continue to email <ArrowRight size={16} />
            </Button>
            {!allChecked && <p className="mt-2 text-center text-xs text-ash">Tick all items to continue</p>}
          </div>
        </aside>
      </div>
    </AppShell>
  );
}

function TabBtn({ active, children, onClick, icon: Icon }: { active: boolean; children: React.ReactNode; onClick: () => void; icon: typeof FileText }) {
  return (
    <button
      onClick={onClick}
      className={`-mb-px inline-flex items-center gap-1.5 border-b-2 px-4 py-2.5 text-sm font-medium transition-colors ${
        active ? "border-brand-green text-brand-green-strong" : "border-transparent text-mute hover:text-body"
      }`}
    >
      <Icon size={15} /> {children}
    </button>
  );
}
