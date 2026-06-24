"use client";

import Link from "next/link";
import { LayoutDashboard, History } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { UserMenu } from "@/components/UserMenu";

const NAV: { href: string; label: string; icon: LucideIcon; key: string }[] = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, key: "dashboard" },
  { href: "/history", label: "History", icon: History, key: "history" },
];

function Logo() {
  return (
    <Link href="/dashboard" className="flex items-center gap-2.5">
      <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-green to-brand-green-strong text-white shadow-sm">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
          <path d="M12 22v-7" /><path d="M9 9a3 3 0 0 1 6 0c1.7 0 3 1.3 3 3a3 3 0 0 1-3 3H9a3 3 0 0 1 0-6Z" />
        </svg>
      </span>
      <span className="leading-tight">
        <span className="block text-[15px] font-semibold tracking-tight text-ink">Contracts</span>
        <span className="hidden text-[11px] font-medium text-mute sm:block">Taleemabad · P&amp;C</span>
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
      className={`inline-flex items-center gap-2 rounded-full px-3.5 py-2 text-sm font-semibold transition-colors ${
        isActive ? "bg-cream-card text-ink" : "text-mute hover:bg-cream-card hover:text-ink"
      }`}
    >
      <Icon size={17} strokeWidth={2} />
      <span className="hidden sm:inline">{item.label}</span>
    </Link>
  );
}

export function AppShell({ children, active }: { children: React.ReactNode; active?: string }) {
  return (
    <div className="min-h-dvh">
      <header className="sticky top-0 z-30 border-b border-hairline bg-cream-soft/85 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-3 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2 sm:gap-5">
            <Logo />
            <nav className="flex items-center gap-1">
              {NAV.map((item) => (
                <NavItem key={item.key} item={item} active={active} />
              ))}
            </nav>
          </div>
          <UserMenu />
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">{children}</main>
    </div>
  );
}
