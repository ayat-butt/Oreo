"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
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

  if (err) return <AppShell active="dashboard"><div className="text-danger">{err}</div></AppShell>;
  if (!p) return <AppShell active="dashboard"><div className="text-slate-500">Loading email…</div></AppShell>;

  return (
    <AppShell active="dashboard">
      <div className="mb-4">
        <Link href={`/draft/${params.requestId}/preview`} className="text-sm text-slate-500 hover:text-slate-700">← Back to preview</Link>
        <h1 className="mt-1 font-serif text-2xl font-semibold text-slate-900">Welcome email</h1>
        <p className="mt-1 text-sm text-slate-500">This is exactly what the candidate receives. Recipients are confirmed on the next step.</p>
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-xl border border-slate-200 bg-white shadow-card">
          <div className="space-y-1 border-b border-slate-100 px-5 py-3 text-sm">
            <div><span className="text-slate-400">Subject</span> · <span className="font-medium text-slate-800">{p.subject}</span></div>
            <div><span className="text-slate-400">To</span> · <span className="text-slate-700">{p.to ?? "—"}</span></div>
            {p.cc.length > 0 && <div><span className="text-slate-400">Cc</span> · <span className="text-slate-700">{p.cc.join(", ")}</span></div>}
          </div>
          <div className="px-5 py-4 text-sm" dangerouslySetInnerHTML={{ __html: p.html_body }} />
        </div>

        <aside className="lg:col-span-1 space-y-4">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-card">
            <h2 className="font-serif text-base font-semibold text-slate-900">Attachments</h2>
            <ul className="mt-3 space-y-2">
              {p.attachments.map((a) => (
                <li key={a} className="flex items-center gap-2 text-sm text-slate-700">
                  <span className="flex h-7 w-7 items-center justify-center rounded bg-red-50 text-[10px] font-semibold text-danger">PDF</span>
                  {a}
                </li>
              ))}
            </ul>
          </div>
          <Button className="w-full" onClick={() => router.push(`/draft/${params.requestId}/send`)}>
            Continue to send →
          </Button>
        </aside>
      </div>
    </AppShell>
  );
}
