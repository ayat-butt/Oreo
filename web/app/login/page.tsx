const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8011";

function GoogleG() {
  return (
    <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden>
      <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z" />
      <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" />
      <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z" />
      <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" />
    </svg>
  );
}

export default function LoginPage({ searchParams }: { searchParams: { error?: string } }) {
  return (
    <div className="flex min-h-dvh items-center justify-center px-4">
      <div className="animate-fade-up w-full max-w-sm rounded-3xl border border-hairline bg-white p-8 text-center shadow-md">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-green to-brand-green-strong text-white shadow-sm">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
            <path d="M12 22v-7" /><path d="M9 9a3 3 0 0 1 6 0c1.7 0 3 1.3 3 3a3 3 0 0 1-3 3H9a3 3 0 0 1 0-6Z" />
          </svg>
        </div>
        <h1 className="mt-5 text-2xl font-semibold tracking-tight text-ink">Contracts Portal</h1>
        <p className="mt-1 text-sm text-mute">Taleemabad · People &amp; Culture</p>

        {searchParams.error === "not_allowed" && (
          <p className="mt-5 rounded-xl bg-danger-soft px-3 py-2.5 text-sm text-danger" role="alert">
            That account isn’t on the access list. Ask Ayat to add you.
          </p>
        )}

        <a
          href={`${API_BASE}/auth/login`}
          className="mt-6 inline-flex w-full items-center justify-center gap-2.5 rounded-xl border border-hairline bg-white px-4 py-3 text-sm font-semibold text-body transition-colors hover:bg-cream-card focus:outline-none focus:ring-4 focus:ring-brand-green/20"
        >
          <GoogleG /> Continue with Google
        </a>
        <p className="mt-4 text-xs text-ash">@taleemabad.com accounts only</p>
      </div>
    </div>
  );
}
