// Status pill — color + label + dot (never color alone, per a11y rule color-not-only).

const STYLES: Record<string, { bg: string; text: string; dot: string; label: string }> = {
  offer:   { bg: "bg-blue-50",   text: "text-brand-blue-strong", dot: "bg-brand-blue",   label: "Offer extended" },
  hired:   { bg: "bg-green-50",  text: "text-brand-green-strong", dot: "bg-brand-green", label: "Hired" },
  ready:   { bg: "bg-green-50",  text: "text-brand-green-strong", dot: "bg-brand-green", label: "Ready to draft" },
  pending: { bg: "bg-slate-100", text: "text-slate-600",         dot: "bg-slate-400",   label: "Awaiting details" },
};

export function StatusBadge({ kind }: { kind: keyof typeof STYLES | string }) {
  const s = STYLES[kind] ?? STYLES.pending;
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${s.bg} ${s.text}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${s.dot}`} aria-hidden />
      {s.label}
    </span>
  );
}
