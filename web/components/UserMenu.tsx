"use client";

import { useEffect, useState } from "react";
import { API_BASE } from "@/lib/client";

export function UserMenu() {
  const [me, setMe] = useState<{ email: string; name: string } | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/auth/me`, { credentials: "include" })
      .then((r) => (r.ok ? r.json() : null))
      .then(setMe)
      .catch(() => {});
  }, []);

  async function logout() {
    try {
      await fetch(`${API_BASE}/auth/logout`, { method: "POST", credentials: "include" });
    } catch {}
    window.location.href = "/login";
  }

  const label = me?.name || me?.email || "Signed in (dev)";
  const initial = (me?.name || me?.email || "D").trim().charAt(0).toUpperCase();

  return (
    <div className="flex items-center gap-2 rounded-lg px-2 py-2">
      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-200 text-xs font-semibold text-slate-700">
        {initial}
      </span>
      <div className="min-w-0 leading-tight">
        <div className="truncate text-sm font-medium text-slate-800">{label}</div>
        <button onClick={logout} className="text-[11px] text-slate-500 hover:text-slate-700">
          Log out
        </button>
      </div>
    </div>
  );
}
