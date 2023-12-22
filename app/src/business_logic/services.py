from datetime import datetime, timedelta
from typing import List, Tuple
import logging
from sqlalchemy.orm import Session
from jose import jwt

from src.config.app_config import Config
from src.routes.dto import RegistrationData, Guest as GuestDto, EmailVerificationDate
from src.database.db_tables import User, Guest
from src.database.models.user_status import UserStatus
from src.database.models.guest_status import GuestStatus
from src.security import hash_token, generate_token, hash_password, verify_password


class Service():

    def __init__(self, db: Session, config: Config) -> None:
        self.db = db
        self.config = config

    def register_user(self, registration_data: RegistrationData) -> Tuple[User, str]:

        hashed_token = hash_token(registration_data.invitation_token)
        user = self.db.query(User).filter_by(invitation_hash=hashed_token).first()

        # User registration only allowed for users which are unseen or unverified
        if not user or user.status not in {UserStatus.UNSEEN, UserStatus.UNVERIFIED}:
            raise AttributeError()

        try:
            email_token = generate_token()

            user.email = registration_data.email
            user.password_hash = hash_password(registration_data.password)
            user.email_verification_hash = hash_token(email_token)
            user.status = UserStatus.UNVERIFIED

            self.db.commit()
            self.db.refresh(user)
            return user, email_token
        except Exception:
            self.db.rollback()
            raise AttributeError()

    def verify_email(self, email_verification: EmailVerificationDate) -> str:
        try:
            hashed_token = hash_token(email_verification.token)
            user = self.db.query(User).filter_by(email_verification_hash=hashed_token).first()

            # E-Mail verification is only allowed for unverified users
            if not user or user.status != UserStatus.UNVERIFIED:
                raise AttributeError()

            user.status = UserStatus.VERIFIED
            self.db.commit()
            self.db.refresh(user)

            return self._create_access_token(user.email)
        except Exception:
            self.db.rollback()
            raise AttributeError()

    def login(self, email: str, password: str) -> str:
        user = self.db.query(User).filter_by(email=email).first()

        # Only verified user can login
        if not user or not user.email or user.status not in {UserStatus.VERIFIED}:
            raise AttributeError()
        if not verify_password(password, user.password_hash):
            raise AttributeError()

        return self._create_access_token(email=user.email)

    def get_guests_of_user(self, user: User) -> List[Guest]:
        guests = []
        for guest in user.associated_guests:
            status = not (guest.status == GuestStatus.EXCUSED)

            guests.append(GuestDto(id=guest.id, first_name=guest.first_name,
                                   last_name=guest.last_name, joins=status,
                                   food_option=guest.food_option,
                                   allergies=guest.allergies))
        return guests

    def update_guests_of_user(self, guests: List[GuestDto], user: User) -> None:
        # Check if only guest associated with the logged in user are changed
        allowed_ids = set(associated_guest.id for associated_guest in user.associated_guests)
        received_ids = set(guest.id for guest in guests)

        if received_ids - allowed_ids:
            raise AttributeError()

        try:
            self.db.begin()

            for guest_dto in guests:
                user = self.db.get(Guest).filter_by(id=guest_dto.id).first()

                user.food_option = guest_dto.food_option
                user.allergies = guest_dto.allergies
                user.status = GuestStatus.REGISTERED if guest_dto.joins else GuestStatus.EXCUSED

            self.db.commit()
        except Exception:
            logging.error(f'Failed to register user {guest_dto}')
            self.db.rollback()
            raise AttributeError()

    def _create_access_token(self, email: str):
        data = {'sub': email}
        to_encode = data.copy()
        expires_delta = timedelta(minutes=self.config.api.access_token_expire_minutes)
        to_encode.update({'exp': datetime.utcnow() + expires_delta})
        encoded_jwt = jwt.encode(to_encode,
                                 key=self.config.api.secret_key,
                                 algorithm=self.config.api.algorithm)
        return encoded_jwt
