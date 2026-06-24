"use client";

import { useEffect, useRef, useState } from "react";
import { LogOut, ChevronDown } from "lucide-react";
import { API_BASE } from "@/lib/client";

export function UserMenu() {
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
        className="flex items-center gap-2 rounded-full py-1 pl-1 pr-1 transition-colors hover:bg-cream-card sm:pr-2.5"
      >
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-green to-brand-green-strong text-sm font-semibold text-white">
          {initial}
        </span>
        <span className="hidden min-w-0 max-w-[10rem] leading-tight sm:block">
          <span className="block truncate text-sm font-semibold text-ink">{label}</span>
        </span>
        <ChevronDown size={15} className="hidden text-ash sm:block" />
      </button>
      {open && (
        <div className="absolute right-0 top-[calc(100%+0.5rem)] z-40 w-60 overflow-hidden rounded-2xl border border-hairline bg-white shadow-pop">
          <div className="border-b border-hairline px-4 py-3">
            <div className="truncate text-sm font-semibold text-ink">{label}</div>
            <div className="truncate text-xs text-mute">{me?.email ?? ""}</div>
          </div>
          <button
            onClick={logout}
            className="flex w-full items-center gap-2.5 px-4 py-3 text-sm font-medium text-body transition-colors hover:bg-cream-card"
          >
            <LogOut size={15} /> Log out
          </button>
        </div>
      )}
    </div>
  );
}
