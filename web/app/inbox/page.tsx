"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { motion, type Variants } from "framer-motion";
import {
  Inbox, Mail, RefreshCw, Search, Wallet, CalendarDays, Briefcase,
  ChevronRight, AlertTriangle, X, Loader2,
} from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { StatusBadge } from "@/components/StatusBadge";
import { apiGet, apiPost } from "@/lib/client";
import type { EmailCandidate, EmailCandidatesResponse, IngestResult } from "@/lib/types";

const MotionLink = motion(Link);
const container: Variants = { hidden: {}, show: { transition: { staggerChildren: 0.035 } } };
const item: Variants = { hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0, transition: { duration: 0.25, ease: "easeOut" } } };

function fmtDate(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return isNaN(d.getTime()) ? "" : d.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}

function Stat({ icon: Icon, label, value, accent }: { icon: typeof Inbox; label: string; value: number; accent?: boolean }) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-slate-200/70 bg-white px-4 py-3 shadow-card">
      <span className={`flex h-10 w-10 items-center justify-center rounded-xl ${accent ? "bg-amber-50 text-warning" : "bg-brand-blue-soft text-brand-blue-strong"}`}>
        <Icon size={18} strokeWidth={2} />
      </span>
      <div>
        <div className="text-xl font-semibold tabular-nums text-slate-900">{value}</div>
        <div className="text-[11px] font-medium uppercase tracking-wide text-slate-500">{label}</div>
      </div>
    </div>
  );
}

function Card({ c, onDismiss }: { c: EmailCandidate; onDismiss: (id: string) => void }) {
  const initial = (c.name || "?").trim().charAt(0).toUpperCase();
  return (
    <MotionLink
      variants={item}
      href={`/inbox/${c.id}/form`}
      className="group relative flex flex-col gap-3 rounded-2xl border border-slate-200/70 bg-white p-4 shadow-card transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300/80 hover:shadow-hover"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex min-w-0 items-center gap-3">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-green/20 to-brand-blue/20 text-sm font-semibold text-slate-700">
            {initial}
          </span>
          <div className="min-w-0">
            <div className="truncate font-semibold text-slate-900">{c.name ?? "(name not found)"}</div>
            <div className="truncate text-xs text-slate-500">{c.role ?? "—"}</div>
          </div>
        </div>
        {c.status === "new" ? (
          <button
            onClick={(e) => { e.preventDefault(); e.stopPropagation(); onDismiss(c.id); }}
            className="rounded-lg p-1 text-slate-300 transition-colors hover:bg-slate-100 hover:text-slate-600"
            aria-label="Dismiss"
            title="Dismiss — not a real hire"
          >
            <X size={16} />
          </button>
        ) : (
          <ChevronRight size={18} className="mt-1 shrink-0 text-slate-300 transition-all group-hover:translate-x-0.5 group-hover:text-brand-green" />
        )}
      </div>

      <div className="flex flex-wrap items-center gap-1.5">
        <StatusBadge kind={c.status === "new" ? "review" : c.status === "drafted" ? "drafted" : "pending"} />
      </div>

      <div className="flex flex-col gap-1 text-xs text-slate-500">
        {c.personal_email && (
          <span className="inline-flex min-w-0 items-center gap-1.5"><Mail size={12} className="shrink-0" /><span className="truncate">{c.personal_email}</span></span>
        )}
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
          {c.gross_salary && <span className="inline-flex items-center gap-1.5"><Wallet size={12} /> PKR {c.gross_salary}</span>}
          {c.joining_date && <span className="inline-flex items-center gap-1.5"><CalendarDays size={12} /> {c.joining_date}</span>}
          {c.department && <span className="inline-flex items-center gap-1.5"><Briefcase size={12} /> {c.department}</span>}
        </div>
      </div>

      <div className="mt-1 border-t border-slate-100 pt-2 text-[11px] text-slate-400">
        from {c.sender || "—"}{c.received_at ? ` · ${fmtDate(c.received_at)}` : ""}
      </div>
    </MotionLink>
  );
}

function SkeletonGrid() {
  return (
    <div className="space-y-7">
      <div className="h-8 w-56 skeleton rounded-lg" />
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
        {[0, 1, 2, 3, 4, 5].map((i) => <div key={i} className="h-40 skeleton rounded-2xl" />)}
      </div>
    </div>
  );
}

export default function InboxPage() {
  const [data, setData] = useState<EmailCandidatesResponse | null>(null);
  const [err, setErr] = useState("");
  const [q, setQ] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [note, setNote] = useState("");

  const load = () => apiGet<EmailCandidatesResponse>("/email-candidates").then(setData).catch((e) => setErr(String(e)));
  useEffect(() => { load(); }, []);

  async function refresh() {
    setRefreshing(true); setNote("");
    try {
      const r = await apiPost<IngestResult>("/email-candidates/refresh", {});
      await load();
      setNote(r.error ? `Couldn’t check email: ${r.error}` : `Checked ${r.mailboxes} mailbox(es) — ${r.ingested} new added.`);
    } catch (e) {
      setNote(String(e));
    } finally {
      setRefreshing(false);
    }
  }

  async function dismiss(id: string) {
    setData((d) => d ? { ...d, candidates: d.candidates.filter((c) => c.id !== id) } : d);
    try { await apiPost(`/email-candidates/${id}/dismiss`, {}); } catch { load(); }
  }

  const candidates = useMemo(() => {
    if (!data) return [];
    const needle = q.trim().toLowerCase();
    if (!needle) return data.candidates;
    return data.candidates.filter((c) =>
      [c.name, c.role, c.personal_email, c.department].some((v) => (v ?? "").toLowerCase().includes(needle))
    );
  }, [data, q]);

  return (
    <AppShell active="inbox">
      {err && !data ? (
        <div className="flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-5 text-amber-900">
          <AlertTriangle size={20} className="mt-0.5 shrink-0" />
          <div>
            <h2 className="font-semibold">Couldn’t load email candidates</h2>
            <p className="mt-1 text-sm">{err}</p>
          </div>
        </div>
      ) : !data ? (
        <SkeletonGrid />
      ) : (
        <>
          <header className="mb-6 flex flex-wrap items-end justify-between gap-4">
            <div>
              <h1 className="font-serif text-[1.75rem] font-semibold tracking-tight text-slate-900">From Email</h1>
              <p className="mt-1 text-sm text-slate-500">
                Offer details emailed to you (outside Markaz), auto-extracted for review before drafting.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Stat icon={Inbox} label="Total" value={data.total} />
              <Stat icon={Mail} label="Needs review" value={data.needs_review} accent />
            </div>
          </header>

          <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
            <div className="relative max-w-md flex-1">
              <Search size={16} className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Search by name, role, or email…"
                className="w-full rounded-xl border border-slate-300/80 bg-white py-2.5 pl-10 pr-3 text-sm shadow-xs transition-all placeholder:text-slate-400 hover:border-slate-400/70 focus:border-brand-green focus:outline-none focus:ring-4 focus:ring-brand-green/15"
              />
            </div>
            <button
              onClick={refresh}
              disabled={refreshing}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-xs transition-all hover:bg-slate-50 hover:shadow-sm disabled:opacity-60"
            >
              {refreshing ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
              {refreshing ? "Checking…" : "Check email now"}
            </button>
          </div>

          {note && <p className="mb-4 text-sm text-slate-500">{note}</p>}

          {candidates.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white/60 px-6 py-16 text-center">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
                <Inbox size={24} />
              </span>
              <p className="mt-3 font-medium text-slate-700">{q ? "No matches" : "No offer emails ingested yet"}</p>
              <p className="mt-1 max-w-md text-sm text-slate-500">
                {q ? "Try a different search." : "When an offer email arrives, it appears here automatically. You can also click “Check email now”."}
              </p>
            </div>
          ) : (
            <motion.div variants={container} initial="hidden" animate="show" className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
              {candidates.map((c) => <Card key={c.id} c={c} onDismiss={dismiss} />)}
            </motion.div>
          )}
        </>
      )}
    </AppShell>
  );
}
