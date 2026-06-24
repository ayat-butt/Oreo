// Status pill — icon + label + color (never color alone).
import { CheckCircle2, Clock, Sparkles } from "lucide-react";
import type { LucideIcon } from "lucide-react";

const STYLES: Record<string, { bg: string; text: string; Icon: LucideIcon; label: string }> = {
  offer:   { bg: "bg-brand-blue-soft",  text: "text-brand-blue-strong",  Icon: Clock,        label: "Offer extended" },
  hired:   { bg: "bg-brand-green-soft", text: "text-brand-green-strong", Icon: CheckCircle2, label: "Hired" },
  ready:   { bg: "bg-brand-green-soft", text: "text-brand-green-strong", Icon: Sparkles,     label: "Ready to draft" },
  pending: { bg: "bg-cream-deep",       text: "text-mute",               Icon: Clock,        label: "Awaiting details" },
};

export function StatusBadge({ kind }: { kind: keyof typeof STYLES | string }) {
  const s = STYLES[kind] ?? STYLES.pending;
  const Icon = s.Icon;
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${s.bg} ${s.text}`}
    >
      <Icon size={13} strokeWidth={2.5} aria-hidden />
      {s.label}
    </span>
  );
}
