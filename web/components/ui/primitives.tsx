import * as React from "react";
import { Search } from "lucide-react";
import type { LucideIcon } from "lucide-react";

export const inputClass =
  "w-full rounded-xl border border-hairline bg-white px-3.5 py-2.5 text-sm text-ink " +
  "transition-all placeholder:text-ash hover:border-stone " +
  "focus:border-brand-green focus:outline-none focus:ring-4 focus:ring-brand-green/15 " +
  "disabled:bg-cream-card disabled:text-ash";

export function Button({
  variant = "primary",
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "danger" | "ghost";
}) {
  // Flat, confident buttons (Pinterest): color shift on hover, no lift; clear focus ring.
  const base =
    "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold " +
    "transition-colors duration-150 focus:outline-none focus:ring-4 " +
    "active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100";
  const variants: Record<string, string> = {
    primary: "bg-brand-green-strong text-white hover:bg-brand-green focus:ring-brand-green/25",
    secondary: "bg-cream-deep text-ink hover:bg-cream-deeper focus:ring-stone/40",
    danger: "bg-danger text-white hover:bg-red-700 focus:ring-danger/25",
    ghost: "text-body hover:bg-cream-card focus:ring-stone/40",
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
      className={`rounded-xl border border-hairline bg-white ${
        hover ? "transition-all duration-200 hover:border-stone hover:shadow-md" : ""
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
    <section className="rounded-xl border border-hairline bg-white p-6">
      <div className="flex items-center gap-3">
        {Icon && (
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand-green-soft text-brand-green-strong">
            <Icon size={18} strokeWidth={2} />
          </span>
        )}
        <div>
          <h2 className="text-lg font-semibold tracking-tight text-ink">{title}</h2>
          {subtitle && <p className="mt-0.5 text-sm text-mute">{subtitle}</p>}
        </div>
      </div>
      <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">{children}</div>
    </section>
  );
}

export function SourceChip({ source }: { source: "Markaz" | "Manual" }) {
  const styles =
    source === "Markaz" ? "bg-brand-blue-soft text-brand-blue-strong" : "bg-cream-deep text-mute";
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
  source?: "Markaz" | "Manual";
  full?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className={full ? "sm:col-span-2" : ""}>
      <label className="flex items-center gap-2 text-sm font-semibold text-body">
        {label}
        {required && <span className="text-danger" aria-hidden>*</span>}
        {source && <SourceChip source={source} />}
      </label>
      <div className="mt-1.5">{children}</div>
      {hint && !error && <p className="mt-1.5 text-xs text-mute">{hint}</p>}
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
        checked ? "border-brand-green/40 bg-brand-green-soft" : "border-hairline bg-cream-soft hover:bg-cream-card"
      }`}
    >
      <span
        className={`mt-0.5 inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors ${
          checked ? "bg-brand-green" : "bg-stone"
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

/** Pill search bar — cream fill, magnifier glyph, expands to white on focus. */
export function SearchBar({
  value,
  onChange,
  placeholder = "Search…",
  className = "",
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  className?: string;
}) {
  return (
    <div className={`group relative ${className}`}>
      <Search
        size={18}
        className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-ash transition-colors group-focus-within:text-mute"
      />
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="h-12 w-full rounded-full border border-transparent bg-cream-card pl-11 pr-4 text-sm text-ink transition-all placeholder:text-ash hover:bg-cream-deep focus:border-hairline focus:bg-white focus:outline-none focus:ring-4 focus:ring-brand-green/15"
      />
    </div>
  );
}

/** Filter chip — pill that flips fully inverted (ink fill, white text) when active. */
export function FilterChip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full px-4 py-2 text-sm font-semibold transition-colors ${
        active
          ? "bg-ink text-white"
          : "bg-cream-card text-body hover:bg-cream-deep"
      }`}
    >
      {children}
    </button>
  );
}
