
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from src.config.app_config import load_config

config = load_config()

db_file_path = config.db.path.joinpath(config.db.filename).absolute()
engine = create_engine(f"sqlite:///{db_file_path}", echo=True, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
