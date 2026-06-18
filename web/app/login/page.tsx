const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8011";

export default function LoginPage({ searchParams }: { searchParams: { error?: string } }) {
  return (
    <div className="flex min-h-dvh items-center justify-center bg-[var(--bg)] px-4">
      <div className="w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-card">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-brand-green/15 text-brand-green-strong">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
            <path d="M12 22v-7" /><path d="M9 9a3 3 0 0 1 6 0c1.7 0 3 1.3 3 3a3 3 0 0 1-3 3H9a3 3 0 0 1 0-6Z" />
          </svg>
        </div>
        <h1 className="mt-4 font-serif text-2xl font-semibold text-slate-900">Contracts Portal</h1>
        <p className="mt-1 text-sm text-slate-500">Taleemabad · People &amp; Culture</p>

        {searchParams.error === "not_allowed" && (
          <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-danger" role="alert">
            That account isn’t on the access list. Ask Ayat to add you.
          </p>
        )}

        <a
          href={`${API_BASE}/auth/login`}
          className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-brand-green-strong px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-brand-green"
        >
          Continue with Google
        </a>
        <p className="mt-3 text-xs text-slate-400">@taleemabad.com accounts only</p>
      </div>
    </div>
  );
}
