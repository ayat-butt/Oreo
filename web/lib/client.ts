// Client-side API helper. Sends the dev-user header until SSO cookies are wired.
export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8011";
const DEV_HEADERS = { "X-Dev-User": "dev@taleemabad.com" };

function _maybeRedirectLogin(status: number) {
  if (status === 401 && typeof window !== "undefined") window.location.href = "/login";
}

export async function apiGet<T>(path: string): Promise<T> {
  const r = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: { ...DEV_HEADERS },
  });
  if (r.status === 401) _maybeRedirectLogin(401);
  if (!r.ok) throw new Error(`GET ${path} → ${r.status}`);
  return r.json();
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", ...DEV_HEADERS },
    body: JSON.stringify(body),
  });
  if (r.status === 401) _maybeRedirectLogin(401);
  if (!r.ok) {
    let detail = `HTTP ${r.status}`;
    try {
      const j = await r.json();
      detail = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail);
    } catch {}
    throw new Error(detail);
  }
  return r.json();
}
