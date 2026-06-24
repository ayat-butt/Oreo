"use client";

import { useEffect, useRef, useState } from "react";
import { LogOut, ChevronDown } from "lucide-react";
import { API_BASE } from "@/lib/client";

export function UserMenu({ compact = false }: { compact?: boolean }) {
  const [me, setMe] = useState<{ email: string; name: string } | null>(null);
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch(`${API_BASE}/auth/me`, { credentials: "include" })
      .then((r) => (r.ok ? r.json() : null))
      .then(setMe)
      .catch(() => {});
  }, []);

  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", h);
    return () => document.removeEventListener("mousedown", h);
  }, []);

  async function logout() {
    try {
      await fetch(`${API_BASE}/auth/logout`, { method: "POST", credentials: "include" });
    } catch {}
    window.location.href = "/login";
  }

  const label = me?.name || me?.email || "Signed in";
  const initial = (me?.name || me?.email || "U").trim().charAt(0).toUpperCase();

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-2.5 rounded-xl px-2 py-2 text-left transition-colors hover:bg-slate-100"
      >
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-slate-600 to-slate-800 text-sm font-semibold text-white">
          {initial}
        </span>
        {!compact && (
          <>
            <span className="min-w-0 flex-1 leading-tight">
              <span className="block truncate text-sm font-medium text-slate-800">{label}</span>
              <span className="block truncate text-[11px] text-slate-500">{me?.email ?? "—"}</span>
            </span>
            <ChevronDown size={15} className="text-slate-400" />
          </>
        )}
      </button>
      {open && (
        <div
          className={`absolute z-40 w-56 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-lg ${
            compact ? "right-0 top-12" : "bottom-[3.25rem] left-0"
          }`}
        >
          <div className="border-b border-slate-100 px-3 py-2.5">
            <div className="truncate text-sm font-medium text-slate-800">{label}</div>
            <div className="truncate text-xs text-slate-500">{me?.email ?? ""}</div>
          </div>
          <button
            onClick={logout}
            className="flex w-full items-center gap-2 px-3 py-2.5 text-sm text-slate-700 transition-colors hover:bg-slate-50"
          >
            <LogOut size={15} /> Log out
          </button>
        </div>
      )}
    </div>
  );
}
