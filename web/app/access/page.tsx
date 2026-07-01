"use client";

import { useEffect, useMemo, useState } from "react";
import { UserPlus, Trash2, ShieldCheck, Crown, Mail, AlertTriangle, Loader2, UserCog } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { Button, inputClass } from "@/components/ui/primitives";
import { apiGet, apiPost, apiPatch, apiDelete } from "@/lib/client";
import type { AccessMember, AccessListResponse } from "@/lib/types";

export default function AccessPage() {
  const [members, setMembers] = useState<AccessMember[] | null>(null);
  const [forbidden, setForbidden] = useState(false);
  const [err, setErr] = useState("");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState("");

  const load = () =>
    apiGet<AccessListResponse>("/access/members")
      .then((d) => { setMembers(d.members); setForbidden(false); })
      .catch((e) => { String(e).includes("403") ? setForbidden(true) : setErr(String(e)); });

  useEffect(() => { load(); }, []);

  const sorted = useMemo(
    () => (members ? [...members].sort((a, b) => Number(b.is_owner) - Number(a.is_owner) || a.email.localeCompare(b.email)) : []),
    [members],
  );

  async function add() {
    const e = email.trim().toLowerCase();
    if (!e) return;
    setBusy(true); setNote(""); setErr("");
    try {
      await apiPost("/access/members", { email: e, name: name.trim() || null });
      setEmail(""); setName(""); setNote(`Access granted to ${e}.`);
      await load();
    } catch (ex) { setErr(String(ex)); }
    finally { setBusy(false); }
  }

  async function toggle(m: AccessMember) {
    setMembers((ms) => ms?.map((x) => (x.id === m.id ? { ...x, is_active: !x.is_active } : x)) ?? ms);
    try { await apiPatch(`/access/members/${m.id}`, { is_active: !m.is_active }); } catch { load(); }
  }

  async function remove(m: AccessMember) {
    if (!confirm(`Remove access for ${m.email}?`)) return;
    setMembers((ms) => ms?.filter((x) => x.id !== m.id) ?? ms);
    try { await apiDelete(`/access/members/${m.id}`); } catch { load(); }
  }

  if (forbidden) {
    return (
      <AppShell active="access">
        <div className="mx-auto max-w-lg rounded-2xl border border-slate-200/70 bg-white p-8 text-center shadow-card">
          <span className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400"><UserCog size={24} /></span>
          <h1 className="mt-4 font-serif text-xl font-semibold text-slate-900">Admins only</h1>
          <p className="mt-1 text-sm text-slate-500">You don’t have permission to manage access. Ask Ayat to grant it.</p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell active="access">
      <header className="mb-6">
        <h1 className="font-serif text-[1.75rem] font-semibold tracking-tight text-slate-900">Access</h1>
        <p className="mt-1 text-sm text-slate-500">Who can sign in to the Contracts Portal. Add a colleague’s Taleemabad email to grant access.</p>
      </header>

      {/* Add member */}
      <div className="mb-6 rounded-2xl border border-slate-200/70 bg-white p-5 shadow-card">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <label className="flex-1">
            <span className="text-sm font-medium text-slate-700">Email</span>
            <input className={`${inputClass} mt-1`} type="email" value={email} placeholder="name@taleemabad.com"
                   onChange={(e) => setEmail(e.target.value)} onKeyDown={(e) => e.key === "Enter" && add()} />
          </label>
          <label className="flex-1">
            <span className="text-sm font-medium text-slate-700">Name <span className="text-slate-400">(optional)</span></span>
            <input className={`${inputClass} mt-1`} value={name} placeholder="Full name"
                   onChange={(e) => setName(e.target.value)} onKeyDown={(e) => e.key === "Enter" && add()} />
          </label>
          <Button onClick={add} disabled={busy || !email.trim()}>
            {busy ? <Loader2 size={16} className="animate-spin" /> : <UserPlus size={16} />} Grant access
          </Button>
        </div>
        <p className="mt-2 text-xs text-slate-500">Only <b>@taleemabad.com</b> accounts can actually sign in (Google org policy). {note && <span className="text-brand-green-strong">· {note}</span>}</p>
        {err && <p className="mt-2 flex items-center gap-1.5 text-sm text-danger" role="alert"><AlertTriangle size={15} /> {err}</p>}
      </div>

      {/* Members */}
      {!members ? (
        <div className="space-y-2">{[0,1,2,3].map((i) => <div key={i} className="h-16 skeleton rounded-2xl" />)}</div>
      ) : (
        <div className="overflow-hidden rounded-2xl border border-slate-200/70 bg-white shadow-card">
          <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Members</h2>
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium tabular-nums text-slate-500">{members.length}</span>
          </div>
          <ul className="divide-y divide-slate-100">
            {sorted.map((m) => (
              <li key={m.id} className="flex items-center gap-3 px-4 py-3">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-green/20 to-brand-blue/20 text-sm font-semibold text-slate-700">
                  {(m.name || m.email).trim().charAt(0).toUpperCase()}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="truncate font-medium text-slate-900">{m.name || m.email}</span>
                    {m.is_owner && <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2 py-0.5 text-[11px] font-semibold text-warning"><Crown size={11} /> Owner</span>}
                    {m.is_admin && !m.is_owner && <span className="inline-flex items-center gap-1 rounded-full bg-brand-blue-soft px-2 py-0.5 text-[11px] font-semibold text-brand-blue-strong"><ShieldCheck size={11} /> Admin</span>}
                    {!m.is_active && <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-500">Disabled</span>}
                  </div>
                  {m.name && <div className="flex items-center gap-1 truncate text-xs text-slate-500"><Mail size={11} /> {m.email}</div>}
                </div>
                {m.is_owner ? (
                  <span className="text-xs text-slate-400">locked</span>
                ) : (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => toggle(m)}
                      className={`inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors ${m.is_active ? "bg-brand-green" : "bg-slate-300"}`}
                      role="switch" aria-checked={m.is_active} title={m.is_active ? "Active — click to disable" : "Disabled — click to enable"}
                    >
                      <span className={`h-5 w-5 rounded-full bg-white shadow-sm transition-transform ${m.is_active ? "translate-x-[22px]" : "translate-x-0.5"}`} />
                    </button>
                    <button onClick={() => remove(m)} className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-red-50 hover:text-danger" title="Remove access">
                      <Trash2 size={16} />
                    </button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </AppShell>
  );
}
