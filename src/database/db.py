from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.app_config import load_config


def get_db():
    config = load_config()

    engine = create_engine(f"sqlite:///{config.db.get_file_path()}",
                           echo=True, connect_args={"check_same_thread": False})

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
