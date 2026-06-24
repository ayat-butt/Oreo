"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { ContractForm, type FormDetail } from "@/components/ContractForm";
import { apiGet } from "@/lib/client";

interface Detail extends FormDetail {
  application_id: number;
  status: string;
  ready_to_draft: boolean;
}

export default function FormPage({ params }: { params: { id: string } }) {
  const [detail, setDetail] = useState<Detail | null>(null);
  const [loadErr, setLoadErr] = useState("");

  useEffect(() => {
    apiGet<Detail>(`/candidates/${params.id}`).then(setDetail).catch((e) => setLoadErr(String(e)));
  }, [params.id]);

  if (loadErr)
    return <AppShell active="dashboard"><div className="text-danger">Failed to load candidate: {loadErr}</div></AppShell>;
  if (!detail)
    return <AppShell active="dashboard"><div className="text-slate-500">Loading candidate…</div></AppShell>;

  return (
    <AppShell active="dashboard">
      <ContractForm
        detail={detail}
        sourceLabel="Markaz"
        back={{ href: "/dashboard", label: "Dashboard" }}
        sourceNote="pre-filled from Markaz where available; complete the manual fields below."
        meta={{ markaz_application_id: Number(params.id), idempotencyKey: `app-${params.id}-${Date.now()}` }}
      />
    </AppShell>
  );
}
