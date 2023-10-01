import sys
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import Annotated

sys.path.append('/workspaces/wedding-api/app')

from src.database.db import get_db, Session
from src.database.models import User
from src.security import generate_token, hash_token, hash_password, verify_password
from src.email_sender import send_verification_email
from src.config.app_config import config


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app_v1 = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:4200",
    "http://172.18.0.1",
]
if config.frontend_base_url:
    origins.append(config.frontend_base_url)

app_v1.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_access_token(user: User, expires_delta: timedelta = timedelta(minutes=15)):
    data = {'sub': user.email}
    to_encode = data.copy()
    to_encode.update({'exp': datetime.utcnow() + expires_delta})
    encoded_jwt = jwt.encode(to_encode, key=config.api.secret_key, algorithm=config.api.algorithm)
    return encoded_jwt


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



@app_v1.post('/email-verification')
async def verify_email(token: EmailVerificationDate, db: Session = Depends(get_db)):

    hashed_token = hash_token(token.token)
    user = db.query(User).filter_by(email_verification_hash=hashed_token).first()

    if not user:
        raise HTTPException(status_code=404, detail='Token is invalid')

    user.status = 2
    db.commit()
    db.refresh(user)


    access_token = create_access_token(user=user, expires_delta=timedelta(minutes=config.api.access_token_expire_minutes))

    return {'access_token': access_token, 'token_type': 'bearer'}

@app_v1.get('/ping')
async def ping():
    return {'message': 'pong'}

@app_v1.post('/user-register')
async def register_user(background_task: BackgroundTasks, data: RegistrationData, db: Session = Depends(get_db)):
    hashed_token = hash_token(data.invitation_token)
    user = db.query(User).filter_by(invitation_hash=hashed_token).first()


    if not user:
        raise HTTPException(status_code=404, detail='Token is invalid')

    try:
        email_token = generate_token()

        user.email = data.email
        user.password_hash = hash_password(data.password)
        user.email_verification_hash = hash_token(email_token)
        user.status = 1

        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail='User registration failed')
    
    background_task.add_task(func=send_verification_email, receiver_email=user.email, verification_token=email_token)
    print(email_token)

    return {'status': 'success', 'message': 'Verification email send'}

def authenticate_user(email: str, password: str, db: Session):
    user = db.query(User).filter_by(email=email).first()

    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail='Could not validate credentials',
                                          headers={'WWW-Authenticate': 'Bearer'})
    try:
        payload = jwt.decode(token, key=config.api.secret_key, algorithms=config.api.algorithm)
        email: str = payload.get('sub')
        if email is None:
            raise credentials_exception
    
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter_by(email=email).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.status != 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Inactive user')
    return current_user
        

@app_v1.post('/login')
async def login(data: LoginData, db: Session = Depends(get_db)):
    user = authenticate_user(data.email, data.password, db)

    # Todo: Check user status
    if not user or not user.email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", 
                            headers={"WWW-Autenticate": "Bearer"})

    access_token = create_access_token(user=user, expires_delta=timedelta(minutes=config.api.access_token_expire_minutes))
    return {'access_token': access_token, 'token_type': 'bearer'}

@app_v1.get('/guest-info')
async def guest_info(current_user: Annotated[User, Depends(get_current_active_user)]):
    guests = []
    for guest in current_user.associated_guests:
        guests.append(Guest(id=guest.id, first_name=guest.first_name, last_name=guest.last_name, 
                            food_option=guest.food_option, allergies=guest.allergies))

    return {'guests': guests}



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app=app_v1, host='0.0.0.0', port=8000)