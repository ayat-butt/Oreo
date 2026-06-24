"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { motion, type Variants } from "framer-motion";
import { Users, Sparkles, Search, Mail, Briefcase, ChevronRight, Inbox, AlertTriangle } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { StatusBadge } from "@/components/StatusBadge";
import { apiGet } from "@/lib/client";
import type { CandidatesResponse, PipelineCandidate } from "@/lib/types";

const MotionLink = motion(Link);
const container: Variants = { hidden: {}, show: { transition: { staggerChildren: 0.035 } } };
const item: Variants = { hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0, transition: { duration: 0.25, ease: "easeOut" } } };

function Stat({ icon: Icon, label, value, accent }: { icon: typeof Users; label: string; value: number; accent?: boolean }) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-slate-200/70 bg-white px-4 py-3 shadow-card">
      <span className={`flex h-10 w-10 items-center justify-center rounded-xl ${accent ? "bg-brand-green-soft text-brand-green-strong" : "bg-brand-blue-soft text-brand-blue-strong"}`}>
        <Icon size={18} strokeWidth={2} />
      </span>
      <div>
        <div className="text-xl font-semibold tabular-nums text-slate-900">{value}</div>
        <div className="text-[11px] font-medium uppercase tracking-wide text-slate-500">{label}</div>
      </div>
    </div>
  );
}

function CandidateCard({ c }: { c: PipelineCandidate }) {
  const initial = (c.name || "?").trim().charAt(0).toUpperCase();
  return (
    <MotionLink
      variants={item}
      href={`/candidates/${c.application_id}/form`}
      className="group flex flex-col gap-3 rounded-2xl border border-slate-200/70 bg-white p-4 shadow-card transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300/80 hover:shadow-hover"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex min-w-0 items-center gap-3">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-green/20 to-brand-blue/20 text-sm font-semibold text-slate-700">
            {initial}
          </span>
          <div className="min-w-0">
            <div className="truncate font-semibold text-slate-900">{c.name}</div>
            <div className="truncate text-xs text-slate-500">{c.job_title ?? "—"}</div>
          </div>
        </div>
        <ChevronRight size={18} className="mt-1 shrink-0 text-slate-300 transition-all group-hover:translate-x-0.5 group-hover:text-brand-green" />
      </div>
      <div className="flex flex-wrap items-center gap-1.5">
        <StatusBadge kind={c.status} />
        {c.ready_to_draft && <StatusBadge kind="ready" />}
      </div>
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500">
        {c.email && (
          <span className="inline-flex min-w-0 items-center gap-1">
            <Mail size={12} className="shrink-0" />
            <span className="truncate">{c.email}</span>
          </span>
        )}
        {c.engine_employment_type && (
          <span className="inline-flex items-center gap-1">
            <Briefcase size={12} /> {c.engine_employment_type.replace("_", " ")}
          </span>
        )}
      </div>
    </MotionLink>
  );
}

function SkeletonGrid() {
  return (
    <div className="space-y-7">
      <div className="h-8 w-56 skeleton rounded-lg" />
      {[0, 1].map((g) => (
        <div key={g} className="space-y-3">
          <div className="h-4 w-40 skeleton rounded" />
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
            {[0, 1, 2].map((i) => <div key={i} className="h-32 skeleton rounded-2xl" />)}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<CandidatesResponse | null>(null);
  const [err, setErr] = useState("");
  const [q, setQ] = useState("");

  useEffect(() => {
    apiGet<CandidatesResponse>("/candidates").then(setData).catch((e) => setErr(String(e)));
  }, []);

  const groups = useMemo(() => {
    if (!data) return [];
    const needle = q.trim().toLowerCase();
    if (!needle) return data.groups;
    return data.groups
      .map((g) => ({
        ...g,
        candidates: g.candidates.filter((c) =>
          [c.name, c.job_title, c.email, g.department].some((v) => (v ?? "").toLowerCase().includes(needle))
        ),
      }))
      .filter((g) => g.candidates.length > 0);
  }, [data, q]);

  return (
    <AppShell active="dashboard">
      {err ? (
        <div className="flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-5 text-amber-900">
          <AlertTriangle size={20} className="mt-0.5 shrink-0" />
          <div>
            <h2 className="font-semibold">Couldn’t load candidates</h2>
            <p className="mt-1 text-sm">{err}</p>
          </div>
        </div>
      ) : !data ? (
        <SkeletonGrid />
      ) : (
        <>
          <header className="mb-6 flex flex-wrap items-end justify-between gap-4">
            <div>
              <h1 className="font-serif text-[1.75rem] font-semibold tracking-tight text-slate-900">Contract Drafting</h1>
              <p className="mt-1 text-sm text-slate-500">Candidates whose offer was accepted, grouped by department.</p>
            </div>
            <div className="flex gap-3">
              <Stat icon={Users} label="In pipeline" value={data.total} />
              <Stat icon={Sparkles} label="Ready to draft" value={data.ready_to_draft} accent />
            </div>
          </header>

          <div className="relative mb-7 max-w-md">
            <Search size={16} className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search by name, role, email, or department…"
              className="w-full rounded-xl border border-slate-300/80 bg-white py-2.5 pl-10 pr-3 text-sm shadow-xs transition-all placeholder:text-slate-400 hover:border-slate-400/70 focus:border-brand-green focus:outline-none focus:ring-4 focus:ring-brand-green/15"
            />
          </div>

          {groups.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white/60 px-6 py-16 text-center">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
                <Inbox size={24} />
              </span>
              <p className="mt-3 font-medium text-slate-700">{q ? "No matches" : "No accepted offers yet"}</p>
              <p className="mt-1 text-sm text-slate-500">{q ? "Try a different search." : "Candidates appear here once their offer is accepted in Markaz."}</p>
            </div>
          ) : (
            <div className="space-y-8">
              {groups.map((g) => (
                <section key={g.department}>
                  <div className="mb-3 flex items-center gap-2 px-0.5">
                    <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">{g.department}</h2>
                    <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium tabular-nums text-slate-500">{g.candidates.length}</span>
                  </div>
                  <motion.div
                    variants={container}
                    initial="hidden"
                    animate="show"
                    className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3"
                  >
                    {g.candidates.map((c) => <CandidateCard key={c.application_id} c={c} />)}
                  </motion.div>
                </section>
              ))}
            </div>
          )}
        </>
      )}
    </AppShell>
  );
}
