import sys
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List


sys.path.append('/workspaces/wedding-api/app')

from src.database.db import Base

user_role_table = Table(
    'user_role_table',
    Base.metadata,
    Column('role_id', ForeignKey('role_table.id')),
    Column('user_id', ForeignKey('user_table.id'))
)


class Role(Base):
    __tablename__ = 'role_table'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]


class User(Base):
    __tablename__ = 'user_table'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(nullable=True)
    invitation_hash: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)
    email_verification_hash: Mapped[str] = mapped_column(index=True, unique=True, nullable=True)
    last_login: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[int]
    # Relationships

    # 1:n = User : Guest
    associated_guests: Mapped[List["Guest"]] = relationship(back_populates="user")
    
    # m:n = User:Role
    role: Mapped[List['Role']] = relationship(secondary=user_role_table)


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