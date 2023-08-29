import sys
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship
from typing import List


sys.path.append('/workspaces/wedding-api/app')

from src.database.db import Base
from src.code_generator import generate_code


class Invitation(Base):
    __tablename__ = 'invitation_table'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    invitation_hash: Mapped[str]
    email_verification_hash: Mapped[str] = ''
    status: Mapped[int] = 0
    associated_guests: Mapped[List["Guest"]] = relationship(back_populates="invitation")


class Guest(Base):
    __tablename__ = 'guest_table'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[int] = 0
    email: Mapped[str] = ''
    password_hash: Mapped[str] = ''
    first_name: Mapped[str]
    last_name: Mapped[str]
    food_option: Mapped[int] = 0
    allergies: Mapped[str] = ''
    invitation_id: Mapped[int] = mapped_column(ForeignKey("invitation_table.id"))
    invitation: Mapped["Invitation"] = relationship(back_populates="associated_guests")



class User(Base):
    __tablename__ = 'user_table'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str]
    password_hash: Mapped[str]
    last_login: Mapped[str]
    status: Mapped[int]



# with Session(engine) as session:
#     i = Invitation(invitation_hash=generate_code(16))

#     i.associated_guests.append(Guest(first_name='Rafael', last_name='Müller'))
#     i.associated_guests.append(Guest(first_name='Melanie', last_name='Häner'))
    
#     session.add(i)
#     session.commit()