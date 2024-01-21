from pydantic import BaseModel


class RegistrationData(BaseModel):
    invitation_token: str
    email: str
    password: str


class LoginData(BaseModel):
    email: str
    password: str


class EmailVerificationDate(BaseModel):
    token: str


class Guest(BaseModel):
    id: int
    first_name: str
    last_name: str
    joins: bool
    food_option: int
    dessert_option: int
    allergies: str
    favorite_fairy_tale_character: str
    favorite_tool: str
