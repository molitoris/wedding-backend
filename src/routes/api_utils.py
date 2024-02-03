from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from src.business_logic.services import Service

from src.config.app_config import load_config
from src.database.db import get_db
from src.database.db_tables import User
from src.database.models.user_status import UserStatus

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

config = load_config()


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


def get_serivce(db: Session = Depends(get_db)):
    yield Service(db, config)
