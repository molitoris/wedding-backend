from sqlalchemy import Table, Column, ForeignKey, Enum, Integer, String
from sqlalchemy.orm import relationship, mapped_column

from src.database.models.guest_status import GuestStatus
from src.database.models.user_status import UserStatus
from src.database.models.user_role import UserRole
from src.database.models.food_options import FoodOption
from src.database.db_base import Base


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
    user = relationship('User', secondary=user_role_table, back_populates='role')


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
    role = relationship('Role', secondary=user_role_table, back_populates='user')


class Guest(Base):
    __tablename__ = 'guest_table'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String)
    last_name = Column(String)
    food_option = Column(Enum(FoodOption))
    allergies = Column(String)
    status = Column(Enum(GuestStatus))
    favorite_fairy_tale_character = Column(String)
    favorite_tool = Column(String)

    # Relationship

    user_id = mapped_column(ForeignKey('user_table.id'))

    # n:1 = Guest:User
    user = relationship('User', back_populates='associated_guests')
