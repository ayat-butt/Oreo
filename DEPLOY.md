# Deploy — Contracts Portal

**Backend (FastAPI)** → Railway · **Frontend (Next.js)** → Vercel · **App DB** → Neon · **Login** → Google SSO.
Both deploy from this repo, branch `feat/contracts-webapp`.

---

## Step 1 — Push the branch (you)
This shell has no GitHub credentials. From VS Code **Source Control → Push**, or a terminal where your
GitHub auth works:
```
git push -u origin feat/contracts-webapp
```

## Step 2 — Railway (backend)
1. railway.app → **New Project → Deploy from GitHub repo** → pick `ayat-butt/Oreo`, branch `feat/contracts-webapp`.
2. Railway auto-detects `nixpacks.toml` (installs `api/requirements.txt`, starts `uvicorn api.main:app`).
   - Root directory: repo root (leave default).
3. Add the **environment variables** from the table below.
4. Deploy → note the public URL, e.g. `https://oreo-contracts.up.railway.app` → this is **BACKEND_URL**.
5. Check `BACKEND_URL/healthz` → should be `{"status":"ok"}`.

## Step 3 — Vercel (frontend)
1. vercel.com → **Add New Project** → import `ayat-butt/Oreo`.
2. **Root Directory = `web`** (important). Framework auto-detects Next.js.
3. Env var: `NEXT_PUBLIC_API_URL = <BACKEND_URL>`.
4. Deploy → note the URL, e.g. `https://oreo-contracts.vercel.app` → this is **FRONTEND_URL**.

## Step 4 — Google OAuth client (SSO)
Google Cloud Console (taleemabad.com org):
1. **OAuth consent screen** → User type **Internal** → app name "Contracts Portal" → save.
2. **Credentials → Create credentials → OAuth client ID → Web application**:
   - **Authorized JavaScript origins:** `<FRONTEND_URL>` and `<BACKEND_URL>`
   - **Authorized redirect URIs:** `<BACKEND_URL>/auth/callback`
3. Copy the **Client ID** and **Client secret** → set in Railway (Step 5).

## Step 5 — Railway env vars
| Name | Value |
|------|-------|
| `ENVIRONMENT` | `production` |
| `MARKAZ_DB_URL` | *(copy from your local `.env`)* |
| `APP_DATABASE_URL` | *(copy from your local `.env` — the Neon app DB)* |
| `GOOGLE_SERVICE_TOKEN_JSON` | *(paste the full contents of `token.json`)* |
| `GOOGLE_OAUTH_CLIENT_ID` | *(from Step 4)* |
| `GOOGLE_OAUTH_CLIENT_SECRET` | *(from Step 4)* |
| `OAUTH_REDIRECT_URI` | `<BACKEND_URL>/auth/callback` |
| `FRONTEND_URL` | `<FRONTEND_URL>` |
| `CORS_ALLOWED_ORIGINS` | `<FRONTEND_URL>` |
| `JWT_SECRET` | *(generated 48-char secret — see chat)* |
| `ALLOWLIST_EMAILS` | `ayat@taleemabad.com,ahsan.javed@taleemabad.com,ayesha.khan@taleemabad.com,aymen.abid@taleemabad.com,javariya.mufarrakh@taleemabad.com,jawwad.ali@taleemabad.com,mehwish.bibi@taleemabad.com,salman.iqbal@taleemabad.com,zeshan.dhillon@taleemabad.com` |
| `TEST_PILOT_EMAIL` | `ayat@taleemabad.com` |
| `ANTHROPIC_API_KEY` | *(optional — only if AI features are added later)* |

> Access is **deny-by-default**: only the `ALLOWLIST_EMAILS` (the People & Culture team, extracted from Markaz)
> can log in — not every Taleemabad employee. `ALLOWED_LOGIN_DOMAINS` is left empty on purpose. To add/remove a
> P&C member later, just edit `ALLOWLIST_EMAILS` in Railway. (niete-only P&C members — Babar, Shoaib — are not
> included since you asked for Taleemabad-domain accounts; add them here if needed.)

After setting these, redeploy the Railway service.

## Step 6 — App DB tables
The Neon app DB already has its tables (created during development). If you ever point at a fresh DB,
run once: `python -m api.db.init_db` with `APP_DATABASE_URL` set.

## Step 7 — Smoke test
1. Open `<FRONTEND_URL>` → redirected to `/login`.
2. **Continue with Google** → sign in with an allowlisted `@taleemabad.com` account → lands on the dashboard.
3. A non-allowlisted account should be rejected ("not on the access list").
4. Pick a candidate → form (Markaz prefill) → Generate → Preview → Email → **Send Pilot** to `TEST_PILOT_EMAIL`.
5. `Live` send works only with `ENVIRONMENT=production` + explicit confirm.

## Notes
- **Embedded preview** across domains: contracts are owned by `ayat@niete.edu.pk`. For taleemabad users to see
  the embedded Google Doc, move the "CONTRACT FOR AGENT OREO" folder into a **Shared Drive** in the taleemabad
  org with `ayat@niete.edu.pk` as a member (Phase 4). Until then, "Open in Google Docs" works and sending is
  unaffected (PDFs export server-side).
- **Secrets** live only in Railway/Vercel env — never commit `.env`, `token.json`, `credentials.json` (git-ignored).
- The **service-token consent screen** should be **published (Internal)** so the refresh token doesn't expire in ~7 days.
