from enum import Enum, IntEnum
from typing import List

from pydantic import BaseModel, Field

class FoodOption(IntEnum):
    UNDEFINED = 0,
    VEGETARIAN = 1,
    OMNIVORE = 2,

class GuestStatus(IntEnum):
    UNDEFINED = 0,
    REGISTERED = 1,
    EXCUSED = 2
class Guest(BaseModel):
    first_name: str = ''
    last_name: str = ''
    food_option: FoodOption = FoodOption.UNDEFINED
    allergies: List[str] = Field(default_factory=list)
    status: GuestStatus = GuestStatus.UNDEFINED

class RegistrationStatus(IntEnum):
    UNUSED = 0,
    UNCONFIRMED = 1,
    CONFIRMED = 2,
    DELETED = 3


class Invitation(BaseModel):
    id: int
    invitation_code: str = ''
    email: str = ''
    password_hash: str = ''
    status: RegistrationStatus = RegistrationStatus.UNUSED
    email_verification_code: str = ''
    associated_guests: List[Guest] = Field(default_factory=list)

class User(BaseModel):
    email: str
    password_hash: str
    last_login: str
    associated_guest: List = Field(default_factory=list)
    status: RegistrationStatus = RegistrationStatus.UNUSED


