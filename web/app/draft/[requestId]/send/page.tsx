"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { Button, inputClass } from "@/components/ui/primitives";
import { apiGet, apiPost } from "@/lib/client";

interface Preview { subject: string; to: string | null; cc: string[]; attachments: string[]; }
interface SendResult { kind: string; to: string; subject: string; gmail_id: string; request_status: string; }

export default function SendPage({ params }: { params: { requestId: string } }) {
  const [p, setP] = useState<Preview | null>(null);
  const [mode, setMode] = useState<"pilot" | "live">("pilot");
  const [testAddr, setTestAddr] = useState("");
  const [cc, setCc] = useState("");
  const [confirmName, setConfirmName] = useState("");
  const [modal, setModal] = useState(false);
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState<SendResult | null>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    apiGet<Preview>(`/contracts/${params.requestId}/email/preview`).then((d) => {
      setP(d); setCc(d.cc.join(", "));
    }).catch((e) => setErr(String(e)));
  }, [params.requestId]);

  const firstName = (p?.to ? "" : "") || (p && p.subject ? "" : "");
  // candidate first name for typed confirm — derive from To local-part as a hint is unreliable;
  // we require typing the recipient email instead for Live.
  const ccArray = () => cc.split(",").map((s) => s.trim()).filter(Boolean);

  async function doSend() {
    setSending(true); setErr("");
    try {
      if (mode === "pilot") {
        const r = await apiPost<SendResult>(`/contracts/${params.requestId}/email/pilot`,
          { test_address: testAddr || null, cc: ccArray() });
        setResult(r);
      } else {
        const r = await apiPost<SendResult>(`/contracts/${params.requestId}/email/live`,
          { confirm: true, cc: ccArray() });
        setResult(r);
      }
      setModal(false);
    } catch (e) { setErr(String(e)); setModal(false); }
    finally { setSending(false); }
  }

  if (err && !p) return <AppShell active="dashboard"><div className="text-danger">{err}</div></AppShell>;
  if (!p) return <AppShell active="dashboard"><div className="text-slate-500">Loading…</div></AppShell>;

  if (result) {
    return (
      <AppShell active="dashboard">
        <div className="mx-auto max-w-lg rounded-xl border border-green-200 bg-green-50 p-8 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-brand-green text-white">✓</div>
          <h1 className="mt-4 font-serif text-xl font-semibold text-slate-900">
            {result.kind === "pilot" ? "Pilot sent" : "Sent to candidate"}
          </h1>
          <p className="mt-1 text-sm text-slate-600">{result.subject}</p>
          <p className="mt-0.5 text-sm text-slate-500">to {result.to}</p>
          {result.kind === "pilot" && (
            <p className="mt-3 text-sm text-slate-600">Check the test inbox, then come back to send Live.</p>
          )}
          <div className="mt-6 flex justify-center gap-3">
            <Link href="/dashboard"><Button variant="secondary">Back to dashboard</Button></Link>
            {result.kind === "pilot" && <Button onClick={() => { setResult(null); setMode("live"); }}>Proceed to Live →</Button>}
          </div>
        </div>
      </AppShell>
    );
  }

  const recipient = mode === "pilot" ? (testAddr || "the configured test address") : (p.to ?? "the candidate");

  return (
    <AppShell active="dashboard">
      <div className="mb-4">
        <Link href={`/draft/${params.requestId}/email`} className="text-sm text-slate-500 hover:text-slate-700">← Back to email</Link>
        <h1 className="mt-1 font-serif text-2xl font-semibold text-slate-900">Send</h1>
        <p className="mt-1 text-sm text-slate-500">Send a Pilot to yourself first, then Live to the candidate.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <button onClick={() => setMode("pilot")}
          className={`rounded-xl border-2 p-5 text-left transition-colors ${mode === "pilot" ? "border-brand-blue bg-blue-50/50" : "border-slate-200 bg-white hover:border-slate-300"}`}>
          <div className="font-medium text-slate-900">Send Pilot (test)</div>
          <p className="mt-1 text-sm text-slate-500">Sends to a test address with a <code>[TEST]</code> subject. Safe dry run.</p>
        </button>
        <button onClick={() => setMode("live")}
          className={`rounded-xl border-2 p-5 text-left transition-colors ${mode === "live" ? "border-danger bg-red-50/50" : "border-slate-200 bg-white hover:border-slate-300"}`}>
          <div className="font-medium text-slate-900">Send Live (to candidate)</div>
          <p className="mt-1 text-sm text-slate-500">Sends the real email to <b>{p.to ?? "the candidate"}</b>.</p>
        </button>
      </div>

      <div className="mt-5 rounded-xl border border-slate-200 bg-white p-5 shadow-card">
        {mode === "pilot" && (
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Test address</span>
            <input className={`${inputClass} mt-1`} value={testAddr} onChange={(e) => setTestAddr(e.target.value)}
                   placeholder="leave blank to use the server's TEST_PILOT_EMAIL" />
            <p className="mt-1 text-xs text-slate-500">Must be a Taleemabad / NIETE address.</p>
          </label>
        )}
        <label className="mt-4 block">
          <span className="text-sm font-medium text-slate-700">CC (comma-separated)</span>
          <input className={`${inputClass} mt-1`} value={cc} onChange={(e) => setCc(e.target.value)} />
        </label>
        <div className="mt-3 text-sm text-slate-500">
          Attachments: {p.attachments.join(", ")}
        </div>
        {err && <p className="mt-3 text-sm text-danger" role="alert">{err}</p>}
        <div className="mt-5">
          <Button variant={mode === "live" ? "danger" : "primary"} onClick={() => setModal(true)}>
            {mode === "pilot" ? "Send Pilot…" : "Send Live…"}
          </Button>
        </div>
      </div>

      {/* confirm modal */}
      {modal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4" onClick={() => setModal(false)}>
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-pop" onClick={(e) => e.stopPropagation()}>
            <h2 className="font-serif text-lg font-semibold text-slate-900">
              Confirm {mode === "live" ? "LIVE send" : "pilot send"}
            </h2>
            <div className={`mt-3 rounded-lg p-3 text-sm ${mode === "live" ? "bg-red-50 text-red-900" : "bg-blue-50 text-blue-900"}`}>
              <div><b>{mode === "live" ? "LIVE — goes to the candidate" : "PILOT — goes to the test address"}</b></div>
              <div className="mt-1">To: <b>{recipient}</b></div>
              {ccArray().length > 0 && <div>Cc: {ccArray().join(", ")}</div>}
              <div>Attachments: {p.attachments.join(", ")}</div>
            </div>
            {mode === "live" && (
              <label className="mt-4 block">
                <span className="text-sm text-slate-700">Type the recipient email to confirm:</span>
                <input className={`${inputClass} mt-1`} value={confirmName} onChange={(e) => setConfirmName(e.target.value)} placeholder={p.to ?? ""} />
              </label>
            )}
            <div className="mt-5 flex justify-end gap-3">
              <Button variant="secondary" onClick={() => setModal(false)}>Cancel</Button>
              <Button variant={mode === "live" ? "danger" : "primary"} disabled={sending || (mode === "live" && confirmName.trim() !== (p.to ?? ""))}
                      onClick={doSend}>
                {sending ? "Sending…" : mode === "live" ? "Send Live now" : "Send Pilot now"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
