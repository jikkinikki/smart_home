from collections.abc import Generator

from sqlmodel import Session, create_engine

from config.paths import DB_PATH

# check_same_thread=False: FastAPI may use the connection from different threads
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency: `session: Session = Depends(get_session)`."""
    with Session(engine) as session:
        yield session
