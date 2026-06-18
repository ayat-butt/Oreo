"""Create all app DB tables in the configured APP_DATABASE_URL (Neon coco-app).

Run once after setting APP_DATABASE_URL:  python -m api.db.init_db
(For production we'll layer Alembic migrations on top; create_all is fine to bootstrap.)
"""

from api.db.base import Base, engine
from api.db import models  # noqa: F401  (registers tables on Base.metadata)


def main():
    if engine is None:
        raise SystemExit("APP_DATABASE_URL is not set in .env / environment.")
    Base.metadata.create_all(engine)
    print("Tables ensured:")
    for name in sorted(Base.metadata.tables):
        print(f"  - {name}")


if __name__ == "__main__":
    main()
