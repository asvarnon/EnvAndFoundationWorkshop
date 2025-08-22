from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.engine import Engine
from sqlmodel import Field, Session, SQLModel, create_engine, select

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "cache.db"


class CachedItem(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)


def get_engine(echo: bool = False) -> Engine:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{DB_PATH}", echo=echo)


def init_db() -> None:
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


def set_item(key: str, value: str) -> None:
    engine = get_engine()
    with Session(engine) as session:
        item = CachedItem(key=key, value=value)
        session.merge(item)
        session.commit()
    logger.debug("Cache set: key=%s size=%d", key, len(value))


def get_item(key: str) -> str | None:
    engine = get_engine()
    with Session(engine) as session:
        stmt = select(CachedItem).where(CachedItem.key == key)
        logger.debug("statement: %s", stmt)
        result = session.exec(stmt).first()
        if result is None:
            logger.debug("Cache miss: key=%s", key)
            return None
        logger.debug("Cache hit: key=%s", key)
        return result.value
