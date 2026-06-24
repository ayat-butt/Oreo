import * as React from "react";
import type { LucideIcon } from "lucide-react";

export const inputClass =
  "w-full rounded-xl border border-slate-300/80 bg-white px-3.5 py-2.5 text-sm text-slate-900 " +
  "shadow-xs transition-all placeholder:text-slate-400 hover:border-slate-400/70 " +
  "focus:border-brand-green focus:outline-none focus:ring-4 focus:ring-brand-green/15 " +
  "disabled:bg-slate-50 disabled:text-slate-400";

export function Button({
  variant = "primary",
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "danger" | "ghost";
}) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold " +
    "transition-all duration-150 focus:outline-none focus:ring-4 " +
    "active:translate-y-0 active:shadow-sm disabled:opacity-50 disabled:cursor-not-allowed " +
    "disabled:translate-y-0 disabled:shadow-none";
  const variants: Record<string, string> = {
    primary: "bg-brand-green-strong text-white shadow-sm hover:bg-brand-green hover:shadow-md hover:-translate-y-0.5 focus:ring-brand-green/25",
    secondary: "border border-slate-300 bg-white text-slate-700 shadow-xs hover:bg-slate-50 hover:shadow-sm hover:-translate-y-0.5 focus:ring-slate-300/40",
    danger: "bg-danger text-white shadow-sm hover:bg-red-700 hover:shadow-md hover:-translate-y-0.5 focus:ring-danger/25",
    ghost: "text-slate-600 hover:bg-slate-100 focus:ring-slate-300/40",
  };
  return <button className={`${base} ${variants[variant]} ${className}`} {...props} />;
}

export function Card({
  className = "",
  hover = false,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & { hover?: boolean }) {
  return (
    <div
      className={`rounded-2xl border border-slate-200/70 bg-white shadow-card ${
        hover ? "transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300/80 hover:shadow-hover" : ""
      } ${className}`}
      {...props}
    />
  );
}

export function Section({
  title,
  subtitle,
  icon: Icon,
  children,
}: {
  title: string;
  subtitle?: string;
  icon?: LucideIcon;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-2xl border border-slate-200/70 bg-white p-6 shadow-card">
      <div className="flex items-center gap-3">
        {Icon && (
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand-green-soft text-brand-green-strong">
            <Icon size={18} strokeWidth={2} />
          </span>
        )}
        <div>
          <h2 className="font-serif text-lg font-semibold text-slate-900">{title}</h2>
          {subtitle && <p className="mt-0.5 text-sm text-slate-500">{subtitle}</p>}
        </div>
      </div>
      <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">{children}</div>
    </section>
  );
}

export function SourceChip({ source }: { source: "Markaz" | "Email" | "Manual" }) {
  const styles =
    source === "Markaz"
      ? "bg-brand-blue-soft text-brand-blue-strong"
      : source === "Email"
        ? "bg-brand-green-soft text-brand-green-strong"
        : "bg-amber-50 text-warning";
  return (
    <span className={`rounded-md px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${styles}`}>
      {source}
    </span>
  );
}

export function Field({
  label,
  required,
  hint,
  error,
  source,
  full,
  children,
}: {
  label: string;
  required?: boolean;
  hint?: string;
  error?: string;
  source?: "Markaz" | "Email" | "Manual";
  full?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className={full ? "sm:col-span-2" : ""}>
      <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
        {label}
        {required && <span className="text-danger" aria-hidden>*</span>}
        {source && <SourceChip source={source} />}
      </label>
      <div className="mt-1.5">{children}</div>
      {hint && !error && <p className="mt-1.5 text-xs text-slate-500">{hint}</p>}
      {error && <p className="mt-1.5 text-xs font-medium text-danger" role="alert">{error}</p>}
    </div>
  );
}

export function Toggle({
  checked,
  onChange,
  children,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={`flex w-full items-start gap-3 rounded-xl border p-3.5 text-left transition-colors ${
        checked ? "border-brand-green/40 bg-brand-green-soft" : "border-slate-200 bg-slate-50/60 hover:bg-slate-50"
      }`}
    >
      <span
        className={`mt-0.5 inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors ${
          checked ? "bg-brand-green" : "bg-slate-300"
        }`}
      >
        <span
          className={`h-4 w-4 rounded-full bg-white shadow-sm transition-transform ${
            checked ? "translate-x-[18px]" : "translate-x-0.5"
          }`}
        />
      </span>
      <span className="text-sm">{children}</span>
    </button>
  );
}
