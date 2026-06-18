"""Read-only: inspect Markaz jobs.description cleaned text + responsibilities sections."""
import os, re, html, psycopg2, psycopg2.extras
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.getenv("MARKAZ_DB_URL")); conn.set_session(readonly=True, autocommit=True)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def clean(h: str) -> str:
    if not h:
        return ""
    t = re.sub(r"<\s*(p|br|div|li|h[1-6]|tr|ul|ol)[^>]*>", "\n", h, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


for jid in (17, 8, 16, 20):
    cur.execute("SELECT title, description FROM jobs WHERE id=%s", (jid,))
    row = cur.fetchone()
    txt = clean(row["description"])
    hits = [m.start() for m in re.finditer(r"(?i)(key responsibilit|responsibilit|what you.?ll do|role overview|duties|you will)", txt)]
    print(f"=== job {jid}: {row['title']} (clean len {len(txt)}) ===")
    print("heading offsets:", hits[:8])
    if hits:
        s = hits[0]
        print("--- 400 chars from first match ---")
        print(txt[s:s + 400])
    print()
cur.close(); conn.close()
