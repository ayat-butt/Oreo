"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { StatusBadge } from "@/components/StatusBadge";
import { apiGet } from "@/lib/client";
import type { CandidatesResponse, PipelineCandidate } from "@/lib/types";

function CandidateRow({ c }: { c: PipelineCandidate }) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-card transition-colors hover:border-slate-300">
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <span className="truncate font-medium text-slate-900">{c.name}</span>
          <StatusBadge kind={c.status} />
          {c.ready_to_draft && <StatusBadge kind="ready" />}
        </div>
        <div className="mt-0.5 truncate text-sm text-slate-500">
          {c.job_title ?? "—"}
          {c.email ? <span className="text-slate-400"> · {c.email}</span> : null}
          {c.engine_employment_type ? (
            <span className="text-slate-400"> · {c.engine_employment_type.replace("_", " ")}</span>
          ) : null}
        </div>
      </div>
      <Link
        href={`/candidates/${c.application_id}/form`}
        className="shrink-0 rounded-lg bg-brand-green-strong px-3.5 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-green focus:outline-none focus:ring-2 focus:ring-brand-green focus:ring-offset-2"
      >
        Proceed
      </Link>
    </div>
  );
}

function Stat({ label, value, accent }: { label: string; value: number; accent?: boolean }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-center shadow-card">
      <div className={`text-xl font-semibold tnum ${accent ? "text-brand-green-strong" : "text-slate-900"}`}>
        {value}
      </div>
      <div className="text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
    </div>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<CandidatesResponse | null>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    // Fetch in the browser so the cross-site session cookie is sent (credentials: include).
    apiGet<CandidatesResponse>("/candidates").then(setData).catch((e) => setErr(String(e)));
  }, []);

  if (err) {
    return (
      <AppShell active="dashboard">
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-6 text-amber-900">
          <h2 className="font-semibold">Couldn’t load candidates</h2>
          <p className="mt-1 text-sm">{err}</p>
        </div>
      </AppShell>
    );
  }

  if (!data) {
    return (
      <AppShell active="dashboard">
        <div className="space-y-3">
          <div className="h-7 w-56 animate-pulse rounded bg-slate-200" />
          <div className="h-20 animate-pulse rounded-xl bg-slate-100" />
          <div className="h-20 animate-pulse rounded-xl bg-slate-100" />
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell active="dashboard">
      <header className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-serif text-2xl font-semibold text-slate-900">Contract Drafting</h1>
          <p className="mt-1 text-sm text-slate-500">
            Candidates whose offer was accepted, grouped by department.
          </p>
        </div>
        <div className="flex gap-3">
          <Stat label="In pipeline" value={data.total} />
          <Stat label="Ready to draft" value={data.ready_to_draft} accent />
        </div>
      </header>

      {data.groups.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white p-10 text-center text-slate-500">
          No accepted offers in the pipeline yet.
        </div>
      ) : (
        <div className="space-y-7">
          {data.groups.map((g) => (
            <section key={g.department}>
              <div className="mb-2 flex items-center gap-2 px-1">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                  {g.department}
                </h2>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-500 tnum">
                  {g.count}
                </span>
              </div>
              <div className="space-y-2">
                {g.candidates.map((c) => (
                  <CandidateRow key={c.application_id} c={c} />
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </AppShell>
  );
}
