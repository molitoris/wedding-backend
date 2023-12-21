from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.config.app_config import load_config
from src.security import verify_password
from src.database.db import get_db
from src.database.db_tables import User
from src.database.models.user_status import UserStatus

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

config = load_config()


def create_access_token(user: User, expires_delta: timedelta = timedelta(minutes=15)):
    data = {'sub': user.email}
    to_encode = data.copy()
    to_encode.update({'exp': datetime.utcnow() + expires_delta})
    encoded_jwt = jwt.encode(to_encode, key=config.api.secret_key, algorithm=config.api.algorithm)
    return encoded_jwt


def authenticate_user(email: str, password: str, db: Session):
    user = db.query(User).filter_by(email=email).first()

    # Only verified user can login
    if not user or user.status not in {UserStatus.VERIFIED}:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           db: Session = Depends(get_db)):
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
    if current_user.status not in {UserStatus.VERIFIED}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Inactive user')
    return current_user
