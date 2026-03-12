from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from crawler.env import CRAWL_DATA_TVPL_DATABASE_URL
from crawler.env import CRAWL_DATA_ENV_DEV


engine = create_engine(
    CRAWL_DATA_TVPL_DATABASE_URL,
    pool_pre_ping=True,
    echo=CRAWL_DATA_ENV_DEV
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def session_scope():
    """Cung cấp một transactional scope xung quanh một loạt các thao tác."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
