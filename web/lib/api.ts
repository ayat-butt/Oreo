import { cookies } from "next/headers";
import type { CandidatesResponse } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8011";

/** Server-side fetch of the offer pipeline. Forwards the user's session cookie to the API. */
export async function getCandidates(): Promise<CandidatesResponse> {
  const cookieHeader = cookies().toString();
  const res = await fetch(`${API_BASE}/candidates`, {
    cache: "no-store",
    headers: {
      "X-Dev-User": "dev@taleemabad.com", // ignored once SSO is configured
      ...(cookieHeader ? { cookie: cookieHeader } : {}),
    },
  });
  if (res.status === 401) {
    const e = new Error("unauthorized") as Error & { code?: number };
    e.code = 401;
    throw e;
  }
  if (!res.ok) throw new Error(`API ${res.status} fetching candidates`);
  return res.json();
}
