from typing import List
from pydantic import BaseModel, Field


class RegistrationData(BaseModel):
    invitation_token: str
    email: str
    password: str


class LoginData(BaseModel):
    email: str
    password: str


class LoginResponseDto(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")


class EmailVerificationDate(BaseModel):
    token: str


class GuestDto(BaseModel):
    id: int
    first_name: str
    last_name: str
    joins: bool
    food_option: int
    dessert_option: int
    allergies: str
    favorite_fairy_tale_character: str
    favorite_tool: str


class GuestListDto(BaseModel):
    guests: List[GuestDto] = Field(default_factory=list)


class ContactInfoDTO(BaseModel):
    id: int
    first_name: str
    last_name: str

class ContactListDto(BaseModel):
    contacts: List[ContactInfoDTO] = Field(default_factory=list)


class MessageDto(BaseModel):
    receiver_id: int
    subject: str
    message: str
    sender_email: str
    sender_phone: str

class Message(BaseModel):
    subject: str
    message: str
    sender_email: str
    sender_phone: str

