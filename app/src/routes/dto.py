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
    food_option: int
    allergies: str
