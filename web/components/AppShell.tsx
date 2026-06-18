import Link from "next/link";
import { UserMenu } from "@/components/UserMenu";

function NavItem({ href, label, active }: { href: string; label: string; active?: boolean }) {
  return (
    <Link
      href={href}
      className={`block rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
        active ? "bg-brand-green/10 text-brand-green-strong" : "text-slate-600 hover:bg-slate-100"
      }`}
    >
      {label}
    </Link>
  );
}

export function AppShell({ children, active }: { children: React.ReactNode; active?: string }) {
  return (
    <div className="min-h-dvh bg-[var(--bg)]">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 hidden w-60 flex-col border-r border-slate-200 bg-white px-4 py-5 lg:flex">
        <div className="flex items-center gap-2 px-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-green/15 text-brand-green-strong">
            {/* tree mark */}
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
              <path d="M12 22v-7" /><path d="M9 9a3 3 0 0 1 6 0c1.7 0 3 1.3 3 3a3 3 0 0 1-3 3H9a3 3 0 0 1 0-6Z" />
            </svg>
          </span>
          <div className="leading-tight">
            <div className="font-serif text-base font-semibold text-slate-900">Contracts</div>
            <div className="text-[11px] text-slate-500">Taleemabad · P&amp;C</div>
          </div>
        </div>
        <nav className="mt-6 space-y-1">
          <NavItem href="/dashboard" label="Dashboard" active={active === "dashboard"} />
          <NavItem href="/history" label="History" active={active === "history"} />
        </nav>
        <div className="mt-auto">
          <UserMenu />
        </div>
      </aside>

      {/* Main */}
      <div className="lg:pl-60">
        <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
