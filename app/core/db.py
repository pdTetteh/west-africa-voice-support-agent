from collections.abc import Generator

from sqlmodel import SQLModel, Session, create_engine

from app.core.config import settings
from app.core import models  # noqa: F401


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args=connect_args,
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    create_db_and_tables()

    with Session(engine) as session:
        yield session