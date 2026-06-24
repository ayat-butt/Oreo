"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { ContractForm, type FormDetail } from "@/components/ContractForm";
import { apiGet } from "@/lib/client";

interface Detail extends FormDetail {
  id: string;
  status: string;
  source_mailbox: string | null;
  sender: string | null;
  subject: string | null;
  received_at: string | null;
}

export default function EmailCandidateFormPage({ params }: { params: { id: string } }) {
  const [detail, setDetail] = useState<Detail | null>(null);
  const [loadErr, setLoadErr] = useState("");

  useEffect(() => {
    apiGet<Detail>(`/email-candidates/${params.id}`).then(setDetail).catch((e) => setLoadErr(String(e)));
  }, [params.id]);

  if (loadErr)
    return <AppShell active="inbox"><div className="text-danger">Failed to load candidate: {loadErr}</div></AppShell>;
  if (!detail)
    return <AppShell active="inbox"><div className="text-slate-500">Loading candidate…</div></AppShell>;

  return (
    <AppShell active="inbox">
      <ContractForm
        detail={detail}
        sourceLabel="Email"
        back={{ href: "/inbox", label: "From Email" }}
        sourceNote="auto-extracted from the offer email — verify every field before generating."
        meta={{ email_candidate_id: params.id, idempotencyKey: `email-${params.id}-${Date.now()}` }}
      />
    </AppShell>
  );
}
