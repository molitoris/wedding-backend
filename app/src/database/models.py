import sys
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship
from typing import List


sys.path.append('/workspaces/wedding-api/app')

from src.database.db import Base
from src.code_generator import generate_code


class User(Base):
    __tablename__ = 'user_table'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(nullable=True)
    invitation_hash: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)
    email_verification_hash: Mapped[str] = mapped_column(index=True, unique=True, nullable=True)
    last_login: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[int]
    # Relationship
    associated_guests: Mapped[List["Guest"]] = relationship(back_populates="user")


class Guest(Base):
    __tablename__ = 'guest_table'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    food_option: Mapped[int]
    allergies: Mapped[str]
    status: Mapped[int]
    # Relationship
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    user: Mapped["User"] = relationship(back_populates="associated_guests")




# with Session(engine) as session:
#     i = Invitation(invitation_hash=generate_code(16))

#     i.associated_guests.append(Guest(first_name='Rafael', last_name='Müller'))
#     i.associated_guests.append(Guest(first_name='Melanie', last_name='Häner'))
    
#     session.add(i)
#     session.commit()