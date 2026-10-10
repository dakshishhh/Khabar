from collections.abc import Generator

from sqlalchemy import create_engine, make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import get_settings


settings = get_settings()


def normalize_database_url(database_url: str) -> str:
    """Accept hosted Postgres URLs from common providers."""
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    url = make_url(database_url)
    if url.get_backend_name() == "postgresql" and url.host not in {"localhost", "127.0.0.1", "postgres"}:
        query = dict(url.query)
        query.setdefault("sslmode", "require")
        url = url.set(query=query)

    return url.render_as_string(hide_password=False)


engine = create_engine(normalize_database_url(settings.DATABASE_URL), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
