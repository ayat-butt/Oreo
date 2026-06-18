import * as React from "react";

export const inputClass =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 " +
  "shadow-sm placeholder:text-slate-400 focus:border-brand-green focus:outline-none " +
  "focus:ring-2 focus:ring-brand-green/30 disabled:bg-slate-50 disabled:text-slate-400";

export function Button({
  variant = "primary",
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "danger" | "ghost";
}) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium " +
    "transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
  const variants: Record<string, string> = {
    primary: "bg-brand-green-strong text-white hover:bg-brand-green focus:ring-brand-green",
    secondary: "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 focus:ring-slate-300",
    danger: "bg-danger text-white hover:bg-red-700 focus:ring-danger",
    ghost: "text-slate-600 hover:bg-slate-100 focus:ring-slate-300",
  };
  return <button className={`${base} ${variants[variant]} ${className}`} {...props} />;
}

export function Section({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-card">
      <h2 className="font-serif text-lg font-semibold text-slate-900">{title}</h2>
      {subtitle && <p className="mt-0.5 text-sm text-slate-500">{subtitle}</p>}
      <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">{children}</div>
    </section>
  );
}

export function SourceChip({ source }: { source: "Markaz" | "Manual" }) {
  const styles =
    source === "Markaz"
      ? "bg-blue-50 text-brand-blue-strong"
      : "bg-amber-50 text-warning";
  return (
    <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide ${styles}`}>
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
  source?: "Markaz" | "Manual";
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
      <div className="mt-1">{children}</div>
      {hint && !error && <p className="mt-1 text-xs text-slate-500">{hint}</p>}
      {error && <p className="mt-1 text-xs text-danger" role="alert">{error}</p>}
    </div>
  );
}
