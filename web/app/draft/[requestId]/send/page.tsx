"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowLeft, FlaskConical, Send, Paperclip, FileText, Check, CheckCircle2,
  AlertTriangle, Loader2, ShieldAlert, X,
} from "lucide-react";
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

  if (err && !p) return <AppShell active="dashboard"><div className="flex items-center gap-2 rounded-2xl border border-red-200 bg-danger-soft p-5 text-danger"><AlertTriangle size={18} />{err}</div></AppShell>;
  if (!p) return <AppShell active="dashboard"><div className="flex items-center gap-2 text-mute"><Loader2 size={16} className="animate-spin" /> Loading…</div></AppShell>;

  if (result) {
    return (
      <AppShell active="dashboard">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          className="mx-auto max-w-lg rounded-3xl border border-green-200/70 bg-white p-8 text-center"
        >
          <motion.div
            initial={{ scale: 0.6, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "spring", stiffness: 260, damping: 18, delay: 0.05 }}
            className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-green-soft text-brand-green-strong"
          >
            <CheckCircle2 size={30} strokeWidth={2.2} />
          </motion.div>
          <h1 className="mt-4 text-xl font-semibold text-ink">
            {result.kind === "pilot" ? "Pilot sent" : "Sent to candidate"}
          </h1>
          <p className="mt-1 text-sm font-medium text-body">{result.subject}</p>
          <p className="mt-0.5 text-sm text-mute">to {result.to}</p>
          {result.kind === "pilot" && (
            <p className="mx-auto mt-4 max-w-sm rounded-xl bg-brand-blue-soft px-3 py-2.5 text-sm text-brand-blue-strong">
              Check the test inbox, then come back to send Live.
            </p>
          )}
          <div className="mt-6 flex justify-center gap-3">
            <Link href="/dashboard"><Button variant="secondary">Back to dashboard</Button></Link>
            {result.kind === "pilot" && (
              <Button onClick={() => { setResult(null); setMode("live"); }}>
                Proceed to Live <Send size={15} />
              </Button>
            )}
          </div>
        </motion.div>
      </AppShell>
    );
  }

  const recipient = mode === "pilot" ? (testAddr || "the configured test address") : (p.to ?? "the candidate");
  const liveConfirmed = confirmName.trim() === (p.to ?? "");

  return (
    <AppShell active="dashboard">
      <div className="mb-5">
        <Link href={`/draft/${params.requestId}/email`} className="inline-flex items-center gap-1 text-sm text-mute transition-colors hover:text-body"><ArrowLeft size={14} /> Back to email</Link>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-ink">Send</h1>
        <p className="mt-1 text-sm text-mute">Send a Pilot to yourself first, then Live to the candidate.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <ModeCard
          active={mode === "pilot"}
          tone="blue"
          icon={FlaskConical}
          title="Send Pilot (test)"
          desc={<>Sends to a test address with a <code className="rounded bg-cream-deep px-1 py-0.5 text-[12px]">[TEST]</code> subject. Safe dry run.</>}
          onClick={() => setMode("pilot")}
        />
        <ModeCard
          active={mode === "live"}
          tone="red"
          icon={Send}
          title="Send Live (to candidate)"
          desc={<>Sends the real email to <b className="text-body">{p.to ?? "the candidate"}</b>.</>}
          onClick={() => setMode("live")}
        />
      </div>

      <div className="mt-5 rounded-2xl border border-hairline bg-white p-5">
        {mode === "pilot" && (
          <label className="block">
            <span className="text-sm font-medium text-body">Test address</span>
            <input className={`${inputClass} mt-1`} value={testAddr} onChange={(e) => setTestAddr(e.target.value)}
                   placeholder="leave blank to use the server's TEST_PILOT_EMAIL" />
            <p className="mt-1 text-xs text-mute">Must be a Taleemabad / NIETE address.</p>
          </label>
        )}
        <label className={mode === "pilot" ? "mt-4 block" : "block"}>
          <span className="text-sm font-medium text-body">CC (comma-separated)</span>
          <input className={`${inputClass} mt-1`} value={cc} onChange={(e) => setCc(e.target.value)} />
        </label>
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center gap-1.5 text-sm font-medium text-mute"><Paperclip size={14} /> Attachments</span>
          {p.attachments.map((a) => (
            <span key={a} className="inline-flex items-center gap-1.5 rounded-lg border border-hairline bg-cream-card/60 px-2.5 py-1 text-xs text-body">
              <FileText size={13} className="text-danger" /> {a}
            </span>
          ))}
        </div>
        {err && <p className="mt-3 flex items-center gap-1.5 text-sm text-danger" role="alert"><AlertTriangle size={15} /> {err}</p>}
        <div className="mt-5">
          <Button variant={mode === "live" ? "danger" : "primary"} onClick={() => { setConfirmName(""); setModal(true); }}>
            {mode === "pilot" ? <><FlaskConical size={16} /> Send Pilot…</> : <><Send size={16} /> Send Live…</>}
          </Button>
        </div>
      </div>

      {/* confirm modal */}
      <AnimatePresence>
        {modal && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-ink/55 p-4 backdrop-blur-sm"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            onClick={() => !sending && setModal(false)}
          >
            <motion.div
              className="w-full max-w-md rounded-2xl bg-white p-6 shadow-pop"
              initial={{ opacity: 0, scale: 0.95, y: 8 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.97, y: 4 }}
              transition={{ duration: 0.18, ease: "easeOut" }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2.5">
                  <span className={`flex h-9 w-9 items-center justify-center rounded-xl ${mode === "live" ? "bg-danger-soft text-danger" : "bg-brand-blue-soft text-brand-blue-strong"}`}>
                    {mode === "live" ? <ShieldAlert size={18} /> : <FlaskConical size={18} />}
                  </span>
                  <h2 className="text-lg font-semibold text-ink">
                    Confirm {mode === "live" ? "LIVE send" : "pilot send"}
                  </h2>
                </div>
                <button onClick={() => !sending && setModal(false)} className="rounded-lg p-1 text-ash transition-colors hover:bg-cream-deep hover:text-body" aria-label="Close">
                  <X size={18} />
                </button>
              </div>

              <div className={`mt-4 space-y-1 rounded-xl p-3.5 text-sm ${mode === "live" ? "bg-danger-soft text-red-900" : "bg-brand-blue-soft text-blue-900"}`}>
                <div className="font-semibold">{mode === "live" ? "LIVE — goes to the candidate" : "PILOT — goes to the test address"}</div>
                <div className="mt-1">To: <b>{recipient}</b></div>
                {ccArray().length > 0 && <div>Cc: {ccArray().join(", ")}</div>}
                <div>Attachments: {p.attachments.join(", ")}</div>
              </div>

              {mode === "live" && (
                <label className="mt-4 block">
                  <span className="text-sm text-body">Type the recipient email to confirm:</span>
                  <input className={`${inputClass} mt-1`} value={confirmName} onChange={(e) => setConfirmName(e.target.value)} placeholder={p.to ?? ""} autoFocus />
                </label>
              )}

              <div className="mt-5 flex justify-end gap-3">
                <Button variant="secondary" onClick={() => setModal(false)} disabled={sending}>Cancel</Button>
                <Button
                  variant={mode === "live" ? "danger" : "primary"}
                  disabled={sending || (mode === "live" && !liveConfirmed)}
                  onClick={doSend}
                >
                  {sending ? <><Loader2 size={16} className="animate-spin" /> Sending…</>
                    : mode === "live" ? <><Send size={16} /> Send Live now</>
                    : <><Check size={16} /> Send Pilot now</>}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </AppShell>
  );
}

function ModeCard({
  active, tone, icon: Icon, title, desc, onClick,
}: {
  active: boolean; tone: "blue" | "red"; icon: typeof Send;
  title: string; desc: React.ReactNode; onClick: () => void;
}) {
  const ring = tone === "blue" ? "border-brand-blue ring-brand-blue/15" : "border-danger ring-danger/15";
  const badge = active
    ? (tone === "blue" ? "bg-brand-blue-soft text-brand-blue-strong" : "bg-danger-soft text-danger")
    : "bg-cream-deep text-ash";
  return (
    <button
      onClick={onClick}
      className={`group relative rounded-2xl border-2 p-5 text-left transition-all ${active ? `${ring} bg-white ring-4` : "border-hairline bg-white hover:border-stone hover:shadow-card"}`}
    >
      {active && (
        <span className={`absolute right-4 top-4 flex h-5 w-5 items-center justify-center rounded-full text-white ${tone === "blue" ? "bg-brand-blue" : "bg-danger"}`}>
          <Check size={13} strokeWidth={3} />
        </span>
      )}
      <span className={`flex h-10 w-10 items-center justify-center rounded-xl transition-colors ${badge}`}>
        <Icon size={20} />
      </span>
      <div className="mt-3 font-medium text-ink">{title}</div>
      <p className="mt-1 text-sm text-mute">{desc}</p>
    </button>
  );
}
