// Status pill — icon + label + color (never color alone), with a subtle ring.
import { CheckCircle2, Clock, Sparkles } from "lucide-react";
import type { LucideIcon } from "lucide-react";

const STYLES: Record<string, { bg: string; text: string; ring: string; Icon: LucideIcon; label: string }> = {
  offer:   { bg: "bg-brand-blue-soft",  text: "text-brand-blue-strong",  ring: "ring-brand-blue/20",  Icon: Clock,        label: "Offer extended" },
  hired:   { bg: "bg-brand-green-soft", text: "text-brand-green-strong", ring: "ring-brand-green/20", Icon: CheckCircle2, label: "Hired" },
  ready:   { bg: "bg-brand-green-soft", text: "text-brand-green-strong", ring: "ring-brand-green/20", Icon: Sparkles,     label: "Ready to draft" },
  pending: { bg: "bg-slate-100",        text: "text-slate-600",          ring: "ring-slate-200",      Icon: Clock,        label: "Awaiting details" },
};

export function StatusBadge({ kind }: { kind: keyof typeof STYLES | string }) {
  const s = STYLES[kind] ?? STYLES.pending;
  const Icon = s.Icon;
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${s.bg} ${s.text} ${s.ring}`}
    >
      <Icon size={13} strokeWidth={2.5} aria-hidden />
      {s.label}
    </span>
  );
}
