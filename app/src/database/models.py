from sqlalchemy import create_engine
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, Session
from datetime import datetime

Base = declarative_base()

class Invitation(Base):
    __tablename__ = 'invitation'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    invitation_hash: Mapped[str]
    email_verification_hash: Mapped[str]
    status: Mapped[int]


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str]
    password_hash: Mapped[str]
    last_login: Mapped[str]
    status: Mapped[int]


class Guest(Base):
    __tablename__ = 'guest'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[int]
    email: Mapped[str]
    password_hash: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    food_option: Mapped[int]
    allergies: Mapped[str]

engine = create_engine("sqlite:///test.db", echo=True)
# Base.metadata.create_all(engine)

with Session(engine) as session:
    rafa = User(email='rafa.molitoris@gmail.com', password_hash='123', last_login=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status=0)

    session.add(rafa)

    session.commit()