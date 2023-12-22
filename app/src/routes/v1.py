from typing import Annotated, List

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from src.email_sender import send_verification_email
from src.routes.api_utils import get_current_active_user, get_serivce
from src.routes.dto import EmailVerificationDate, Guest as GuestDto, LoginData, RegistrationData
from src.database.db_tables import User
from src.config.app_config import load_config
from src.business_logic.services import Service


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
                        data: RegistrationData,
                        service: Service = Depends(get_serivce)):

    try:
        user, email_token = service.register_user(registration_data=data)

        # Send verification email
        background_task.add_task(func=send_verification_email,
                                 receiver_email=user.email,
                                 verification_token=email_token)
        return {'status': 'success', 'message': 'Verification email send'}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='User registration failed')


@app_v1.post('/email-verification')
async def verify_email(email_verification: EmailVerificationDate,
                       service: Service = Depends(get_serivce)):
    try:
        access_token = service.verify_email(email_verification=email_verification)
        return {'access_token': access_token, 'token_type': 'bearer'}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Email verification failed')


@app_v1.post('/login')
async def login(data: LoginData, service: Service = Depends(get_serivce)):

    try:
        access_token = service.login(data.email, data.password)
        return {'access_token': access_token, 'token_type': 'bearer'}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Autenticate": "Bearer"})


@app_v1.get('/guest-info')
async def guest_info(current_user: Annotated[User, Depends(get_current_active_user)],
                     service: Service = Depends(get_serivce)):
    guests = service.get_guests_of_user(current_user)
    return {'guests': guests}


@app_v1.post('/guest-info')
async def set_guest_info(data: List[GuestDto],
                         current_user: Annotated[User, Depends(get_current_active_user)],
                         service: Service = Depends(get_serivce)) -> str:

    try:
        no_updated_guests = service.update_guests_of_user(guests=data, user=current_user)
        return {'Guests': f'Registered {len(no_updated_guests)} guests'}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect guest",
                            headers={"WWW-Autenticate": "Bearer"})
