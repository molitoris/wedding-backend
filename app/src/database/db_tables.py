import sys

from sqlalchemy import Table, Column, ForeignKey, Enum, Integer, String
from sqlalchemy.orm import relationship, mapped_column

sys.path.append('/workspaces/wedding-api/app')

from src.database.db import Base
from .models.guest_status import GuestStatus
from .models.user_status import UserStatus
from .models.user_role import UserRole


# Intermediate table to store m:n relation
user_role_table = Table(
    'user_role_table',
    Base.metadata,
    Column('role_id', ForeignKey('role_table.id')),
    Column('user_id', ForeignKey('user_table.id'))
)


class Role(Base):
    __tablename__ = 'role_table'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Enum(UserRole))

    # m:n = Role:User
    user = relationship('User', secondary=user_role_table)


class User(Base):
    __tablename__ = 'user_table'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=True)
    invitation_hash = Column(String, index=True, unique=True, nullable=False)
    email_verification_hash = Column(String, index=True, unique=True, nullable=True)
    last_login = Column(String, nullable=True)
    status = Column(Enum(UserStatus))
    # Relationships

    # 1:n = User : Guest
    associated_guests = relationship('Guest', back_populates='user')
    
    # m:n = User:Role
    role = relationship('Role', secondary=user_role_table)


class Guest(Base):
    __tablename__ = 'guest_table'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String)
    last_name = Column(String)
    # TODO(RSM): Exchange with enum
    food_option = Column(Integer)
    allergies = Column(String)
    status = Column(Enum(GuestStatus))
    # Relationship

    user_id = mapped_column(ForeignKey('user_table.id'))

    # n:1 = Guest:User
    user = relationship('User', back_populates='associated_guests')