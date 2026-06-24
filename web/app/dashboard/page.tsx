"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { motion, type Variants } from "framer-motion";
import { Users, Sparkles, Mail, Briefcase, ChevronRight, Inbox, AlertTriangle } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { StatusBadge } from "@/components/StatusBadge";
import { SearchBar, FilterChip } from "@/components/ui/primitives";
import { apiGet } from "@/lib/client";
import type { CandidatesResponse, PipelineCandidate } from "@/lib/types";

const MotionLink = motion(Link);
const container: Variants = { hidden: {}, show: { transition: { staggerChildren: 0.03 } } };
const item: Variants = { hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0, transition: { duration: 0.25, ease: "easeOut" } } };

const AVATARS = [
  "from-brand-green/25 to-brand-green/10 text-brand-green-strong",
  "from-brand-blue/25 to-brand-blue/10 text-brand-blue-strong",
  "from-amber-300/30 to-amber-200/10 text-amber-700",
  "from-rose-300/25 to-rose-200/10 text-rose-700",
  "from-violet-300/25 to-violet-200/10 text-violet-700",
];

function Stat({ icon: Icon, label, value, accent }: { icon: typeof Users; label: string; value: number; accent?: boolean }) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-hairline bg-white px-4 py-3">
      <span className={`flex h-10 w-10 items-center justify-center rounded-xl ${accent ? "bg-brand-green-soft text-brand-green-strong" : "bg-brand-blue-soft text-brand-blue-strong"}`}>
        <Icon size={18} strokeWidth={2} />
      </span>
      <div>
        <div className="text-xl font-semibold tabular-nums text-ink">{value}</div>
        <div className="text-[11px] font-semibold uppercase tracking-wide text-mute">{label}</div>
      </div>
    </div>
  );
}

function CandidateCard({ c, idx }: { c: PipelineCandidate; idx: number }) {
  const initial = (c.name || "?").trim().charAt(0).toUpperCase();
  const avatar = AVATARS[idx % AVATARS.length];
  return (
    <MotionLink
      variants={item}
      href={`/candidates/${c.application_id}/form`}
      className="group mb-4 flex break-inside-avoid flex-col gap-3 rounded-xl border border-hairline bg-white p-4 transition-all duration-200 hover:border-stone hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex min-w-0 items-center gap-3">
          <span className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br text-base font-semibold ${avatar}`}>
            {initial}
          </span>
          <div className="min-w-0">
            <div className="truncate font-semibold text-ink">{c.name}</div>
            <div className="truncate text-xs text-mute">{c.job_title ?? "—"}</div>
          </div>
        </div>
        <ChevronRight size={18} className="mt-1 shrink-0 text-stone transition-all group-hover:translate-x-0.5 group-hover:text-brand-green" />
      </div>
      <div className="flex flex-wrap items-center gap-1.5">
        <StatusBadge kind={c.status} />
        {c.ready_to_draft && <StatusBadge kind="ready" />}
      </div>
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 border-t border-hairline-soft pt-3 text-xs text-mute">
        {c.email && (
          <span className="inline-flex min-w-0 items-center gap-1.5">
            <Mail size={12} className="shrink-0" />
            <span className="truncate">{c.email}</span>
          </span>
        )}
        {c.engine_employment_type && (
          <span className="inline-flex items-center gap-1.5">
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
      <div className="h-10 w-64 skeleton rounded-xl" />
      <div className="h-12 w-full max-w-xl skeleton rounded-full" />
      <div className="columns-1 gap-4 sm:columns-2 xl:columns-3">
        {[0, 1, 2, 3, 4, 5].map((i) => <div key={i} className="mb-4 h-36 skeleton break-inside-avoid rounded-xl" />)}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<CandidatesResponse | null>(null);
  const [err, setErr] = useState("");
  const [q, setQ] = useState("");
  const [dept, setDept] = useState("all");

  useEffect(() => {
    apiGet<CandidatesResponse>("/candidates").then(setData).catch((e) => setErr(String(e)));
  }, []);

  const groups = useMemo(() => {
    if (!data) return [];
    const needle = q.trim().toLowerCase();
    return data.groups
      .filter((g) => dept === "all" || g.department === dept)
      .map((g) => ({
        ...g,
        candidates: !needle
          ? g.candidates
          : g.candidates.filter((c) =>
              [c.name, c.job_title, c.email, g.department].some((v) => (v ?? "").toLowerCase().includes(needle))
            ),
      }))
      .filter((g) => g.candidates.length > 0);
  }, [data, q, dept]);

  return (
    <AppShell active="dashboard">
      {err ? (
        <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-5 text-amber-900">
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
          <header className="flex flex-wrap items-start justify-between gap-5">
            <div>
              <h1 className="text-4xl font-semibold tracking-tightest text-ink sm:text-[2.75rem]">Contract Drafting</h1>
              <p className="mt-2 max-w-xl text-[15px] text-mute">
                Candidates whose offer was accepted, ready to turn into a contract.
              </p>
            </div>
            <div className="flex gap-3">
              <Stat icon={Users} label="In pipeline" value={data.total} />
              <Stat icon={Sparkles} label="Ready to draft" value={data.ready_to_draft} accent />
            </div>
          </header>

          <div className="mt-7">
            <SearchBar value={q} onChange={setQ} placeholder="Search candidates by name, role, or email…" className="max-w-xl" />
          </div>

          {data.groups.length > 1 && (
            <div className="mt-5 flex flex-wrap gap-2">
              <FilterChip active={dept === "all"} onClick={() => setDept("all")}>All</FilterChip>
              {data.groups.map((g) => (
                <FilterChip key={g.department} active={dept === g.department} onClick={() => setDept(g.department)}>
                  {g.department}
                </FilterChip>
              ))}
            </div>
          )}

          {groups.length === 0 ? (
            <div className="mt-10 flex flex-col items-center justify-center rounded-3xl border border-dashed border-stone bg-cream-soft px-6 py-16 text-center">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cream-card text-ash">
                <Inbox size={24} />
              </span>
              <p className="mt-3 font-semibold text-body">{q ? "No matches" : "No accepted offers yet"}</p>
              <p className="mt-1 text-sm text-mute">{q ? "Try a different search." : "Candidates appear here once their offer is accepted in Markaz."}</p>
            </div>
          ) : (
            <div className="mt-8 space-y-9">
              {groups.map((g) => (
                <section key={g.department}>
                  <div className="mb-4 flex items-center gap-2">
                    <h2 className="text-sm font-bold uppercase tracking-wide text-mute">{g.department}</h2>
                    <span className="rounded-full bg-cream-card px-2 py-0.5 text-xs font-semibold tabular-nums text-mute">{g.candidates.length}</span>
                  </div>
                  <motion.div
                    variants={container}
                    initial="hidden"
                    animate="show"
                    className="columns-1 gap-4 sm:columns-2 xl:columns-3"
                  >
                    {g.candidates.map((c, i) => <CandidateCard key={c.application_id} c={c} idx={i} />)}
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
