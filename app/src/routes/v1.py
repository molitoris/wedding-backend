from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Annotated

from src.routes.api_utils import authenticate_user, create_access_token, get_current_active_user
from src.routes.dto import EmailVerificationDate, Guest, LoginData, RegistrationData
from src.database.db import get_db
from src.database.db_tables import User
from src.database.models.user_status import UserStatus
from src.security import generate_token, hash_token, hash_password
from src.email_sender import send_verification_email
from src.config.app_config import load_config


app_v1 = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:4200",
    "http://172.18.0.1",
]

config = load_config()

if config.frontend_base_url:
    origins.append(config.frontend_base_url)

app_v1.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app_v1.get('/ping')
async def ping():
    return {'message': 'pong'}


@app_v1.post('/user-register')
async def register_user(background_task: BackgroundTasks,
                        data: RegistrationData, db: Session = Depends(get_db)):

    hashed_token = hash_token(data.invitation_token)
    user = db.query(User).filter_by(invitation_hash=hashed_token).first()

    # User registration only allowed for users which are unseen or unverified
    if not user or user.status not in {UserStatus.UNSEEN, UserStatus.UNVERIFIED}:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='User registration failed')

    try:
        email_token = generate_token()

        user.email = data.email
        user.password_hash = hash_password(data.password)
        user.email_verification_hash = hash_token(email_token)
        user.status = UserStatus.UNVERIFIED

        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='User registration failed')

    background_task.add_task(func=send_verification_email,
                             receiver_email=user.email,
                             verification_token=email_token)
    print(email_token)

    return {'status': 'success', 'message': 'Verification email send'}


@app_v1.post('/email-verification')
async def verify_email(token: EmailVerificationDate, db: Session = Depends(get_db)):

    hashed_token = hash_token(token.token)
    user = db.query(User).filter_by(email_verification_hash=hashed_token).first()

    # E-Mail verification is only allowed for unverified users
    if not user or user.status != UserStatus.UNVERIFIED:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Email verification failed')

    user.status = UserStatus.VERIFIED
    db.commit()
    db.refresh(user)

    expiration_time = timedelta(minutes=config.api.access_token_expire_minutes)
    access_token = create_access_token(user=user, expires_delta=expiration_time)

    return {'access_token': access_token, 'token_type': 'bearer'}


@app_v1.post('/login')
async def login(data: LoginData, db: Session = Depends(get_db)):
    user = authenticate_user(data.email, data.password, db)

    # Todo: Check user status
    if not user or not user.email or user.status not in {UserStatus.VERIFIED}:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Autenticate": "Bearer"})

    expiration_time = timedelta(minutes=config.api.access_token_expire_minutes)
    access_token = create_access_token(user=user,
                                       expires_delta=expiration_time)
    return {'access_token': access_token, 'token_type': 'bearer'}


@app_v1.get('/guest-info')
async def guest_info(current_user: Annotated[User, Depends(get_current_active_user)]):
    guests = []
    for guest in current_user.associated_guests:
        guests.append(Guest(id=guest.id, first_name=guest.first_name, last_name=guest.last_name,
                            food_option=guest.food_option, allergies=guest.allergies))

    return {'guests': guests}
