"use client";

import Link from "next/link";
import { LayoutDashboard, Inbox, History } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { UserMenu } from "@/components/UserMenu";

const NAV: { href: string; label: string; icon: LucideIcon; key: string }[] = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, key: "dashboard" },
  { href: "/inbox", label: "From Email", icon: Inbox, key: "inbox" },
  { href: "/history", label: "History", icon: History, key: "history" },
];

function Logo() {
  return (
    <Link href="/dashboard" className="flex items-center gap-2.5 px-2">
      <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-green to-brand-green-strong text-white shadow-sm">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
          <path d="M12 22v-7" /><path d="M9 9a3 3 0 0 1 6 0c1.7 0 3 1.3 3 3a3 3 0 0 1-3 3H9a3 3 0 0 1 0-6Z" />
        </svg>
      </span>
      <span className="leading-tight">
        <span className="block font-serif text-base font-semibold text-slate-900">Contracts</span>
        <span className="block text-[11px] font-medium text-slate-500">Taleemabad · P&amp;C</span>
      </span>
    </Link>
  );
}

function NavItem({ item, active }: { item: (typeof NAV)[number]; active?: string }) {
  const Icon = item.icon;
  const isActive = active === item.key;
  return (
    <Link
      href={item.href}
      className={`group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
        isActive ? "bg-brand-green-soft text-brand-green-strong" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
      }`}
    >
      {isActive && <span className="absolute left-0 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r-full bg-brand-green" aria-hidden />}
      <Icon size={18} strokeWidth={2} className={isActive ? "text-brand-green-strong" : "text-slate-400 group-hover:text-slate-600"} />
      {item.label}
    </Link>
  );
}

export function AppShell({ children, active }: { children: React.ReactNode; active?: string }) {
  return (
    <div className="min-h-dvh">
      {/* Mobile top bar */}
      <header className="sticky top-0 z-30 flex items-center justify-between border-b border-slate-200/70 bg-white/80 px-4 py-2.5 backdrop-blur lg:hidden">
        <Logo />
        <UserMenu compact />
      </header>

      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col border-r border-slate-200/70 bg-white/70 px-4 py-5 backdrop-blur-xl lg:flex">
        <Logo />
        <nav className="mt-7 space-y-1">
          {NAV.map((item) => (
            <NavItem key={item.key} item={item} active={active} />
          ))}
        </nav>
        <div className="mt-auto border-t border-slate-200/70 pt-3">
          <UserMenu />
        </div>
      </aside>

      <div className="lg:pl-64">
        <main className="mx-auto max-w-6xl px-4 py-7 sm:px-6 lg:px-10">{children}</main>
      </div>
    </div>
  );
}
