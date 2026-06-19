"""App configuration via environment (pydantic-settings).

Reads from process env (Railway/Vercel) and falls back to the repo .env for local dev.
No secrets are hardcoded here.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Environment
    ENVIRONMENT: str = "development"  # development | preview | production

    # Databases
    MARKAZ_DB_URL: str = ""           # read-only Markaz (existing)
    APP_DATABASE_URL: str = ""        # NEW Neon app DB (drafts/audit/users/jobs)

    # Google service identity (ayat@niete.edu.pk) — full token JSON blob
    GOOGLE_SERVICE_TOKEN_JSON: str = ""

    # Google SSO (taleemabad Internal web client)
    GOOGLE_OAUTH_CLIENT_ID: str = ""
    GOOGLE_OAUTH_CLIENT_SECRET: str = ""
    OAUTH_REDIRECT_URI: str = "http://localhost:8000/auth/callback"

    # App auth
    JWT_SECRET: str = "dev-only-change-me"
    SESSION_COOKIE: str = "coco_session"
    SESSION_TTL_HOURS: int = 12
    ALLOWLIST_EMAILS: str = ""        # comma-separated P&C emails (the access list)
    # Deny-by-default: access is the explicit P&C allowlist, NOT every Taleemabad employee.
    # Set a domain here only if you ever want to open login to a whole domain.
    ALLOWED_LOGIN_DOMAINS: str = ""
    FRONTEND_URL: str = "http://localhost:3000"   # where /auth/callback redirects back to

    # Sending
    TEST_PILOT_EMAIL: str = ""

    # CORS / frontend
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000"

    # AI (optional)
    ANTHROPIC_API_KEY: str = ""

    @property
    def allowlist(self) -> set[str]:
        return {e.strip().lower() for e in self.ALLOWLIST_EMAILS.split(",") if e.strip()}

    @property
    def login_domains(self) -> set[str]:
        return {d.strip().lower() for d in self.ALLOWED_LOGIN_DOMAINS.split(",") if d.strip()}

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]


settings = Settings()
