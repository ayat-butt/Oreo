"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, ArrowRight, Mail, Paperclip, FileText, Loader2 } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { Button } from "@/components/ui/primitives";
import { apiGet } from "@/lib/client";

interface Preview {
  subject: string;
  to: string | null;
  cc: string[];
  html_body: string;
  attachments: string[];
}

export default function EmailPage({ params }: { params: { requestId: string } }) {
  const router = useRouter();
  const [p, setP] = useState<Preview | null>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    apiGet<Preview>(`/contracts/${params.requestId}/email/preview`).then(setP).catch((e) => setErr(String(e)));
  }, [params.requestId]);

  if (err) return <AppShell active="dashboard"><div className="rounded-2xl border border-red-200 bg-danger-soft p-5 text-danger">{err}</div></AppShell>;
  if (!p) return <AppShell active="dashboard"><div className="flex items-center gap-2 text-mute"><Loader2 size={16} className="animate-spin" /> Loading email…</div></AppShell>;

  return (
    <AppShell active="dashboard">
      <div className="mb-5">
        <Link href={`/draft/${params.requestId}/preview`} className="inline-flex items-center gap-1 text-sm text-mute transition-colors hover:text-body"><ArrowLeft size={14} /> Back to preview</Link>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-ink">Welcome email</h1>
        <p className="mt-1 text-sm text-mute">This is exactly what the candidate receives. Recipients are confirmed on the next step.</p>
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
        {/* Mail-style frame */}
        <div className="overflow-hidden rounded-2xl border border-hairline bg-white lg:col-span-2">
          <div className="flex items-center gap-2 border-b border-hairline-soft bg-cream-card/70 px-5 py-3">
            <Mail size={16} className="text-brand-blue-strong" />
            <span className="text-sm font-medium text-body">Message preview</span>
          </div>
          <div className="space-y-1.5 border-b border-hairline-soft px-5 py-3.5 text-sm">
            <div><span className="inline-block w-14 text-ash">Subject</span><span className="font-semibold text-ink">{p.subject}</span></div>
            <div><span className="inline-block w-14 text-ash">To</span><span className="text-body">{p.to ?? "—"}</span></div>
            {p.cc.length > 0 && <div><span className="inline-block w-14 text-ash">Cc</span><span className="text-body">{p.cc.join(", ")}</span></div>}
          </div>
          <div className="px-6 py-5 text-sm leading-relaxed" dangerouslySetInnerHTML={{ __html: p.html_body }} />
        </div>

        <aside className="space-y-4 lg:col-span-1">
          <div className="rounded-2xl border border-hairline bg-white p-5">
            <h2 className="flex items-center gap-2 text-base font-semibold text-ink">
              <Paperclip size={16} className="text-ash" /> Attachments
            </h2>
            <ul className="mt-3 space-y-2">
              {p.attachments.map((a) => (
                <li key={a} className="flex items-center gap-2.5 rounded-xl border border-hairline bg-cream-card/60 px-3 py-2.5 text-sm text-body">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-danger-soft text-danger"><FileText size={16} /></span>
                  <span className="truncate">{a}</span>
                </li>
              ))}
            </ul>
          </div>
          <Button className="w-full" onClick={() => router.push(`/draft/${params.requestId}/send`)}>
            Continue to send <ArrowRight size={16} />
          </Button>
        </aside>
      </div>
    </AppShell>
  );
}
