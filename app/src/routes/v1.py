import sys
from fastapi import FastAPI, Depends, HTTPException, Form
from datetime import datetime, timedelta
from jose import jwt
from pydantic import BaseModel

sys.path.append('/workspaces/wedding-api/app')

from src.database.db import get_db, Session
from src.database.models import User
from src.code_generator import hash_string, generate_code
from src.email_sender import send_verification_email

SECRET_KEY = ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


app_v1 = FastAPI()

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    to_encode.update({'exp': datetime.utcnow() + expires_delta})
    encoded_jwt = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class RegistrationFormData(BaseModel):
        invitation_token: str
        email: str
        password: str


@app_v1.get('/email-verification')
async def verify_email(token: str, db: Session = Depends(get_db)):

    hashed_token = hash_string(token)
    user = db.query(User).filter_by(email_verification_hash=hashed_token).first()

    if not user:
        raise HTTPException(status_code=404, detail='Token is invalid')

    access_token = create_access_token(data={'sub': user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    return {'access_token': access_token, 'token_type': 'bearer'}

@app_v1.post('/user-register')
async def register_user(data: RegistrationFormData, db: Session = Depends(get_db)):
    hashed_token = hash_string(data.invitation_token)
    user = db.query(User).filter_by(invitation_hash=hashed_token).first()

    if not user:
        raise HTTPException(status_code=404, detail='Token is invalid')

    try:
        email_token = generate_code()

        user.email = data.email
        user.password_hash = hash_string(data.password)
        user.email_verification_hash = hash_string(email_token)

        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail='User registration failed')
    
    send_verification_email(user.email, verification_token=email_token)

    return {'status': 'success', 'message': 'Verification email send'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app=app_v1, host='0.0.0.0', port=8000)