from datetime import datetime, timedelta
from typing import List, Tuple
import logging
from sqlalchemy import and_
from sqlalchemy.orm import Session
from jose import jwt

from src.config.app_config import Config
from src.routes.dto import RegistrationData, \
                            GuestDto, \
                            EmailVerificationDate, \
                            ContactInfoDTO, \
                            ContactListDto, \
                            LoginResponseDto, \
                            ForgetPasswordRequestDto, \
                            ForgetPasswordDto, \
                            ResetPasswordRequestDto, \
                            GuestListDto, \
                            MessageDto
from src.database.db_tables import User, Guest, Role
from src.database.models.food_options import FoodOption
from src.database.models.dessert_options import DessertOption
from src.database.models.guest_role import GuestRole
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

    def verify_email(self, email_verification: EmailVerificationDate) -> LoginResponseDto:
        try:
            hashed_token = hash_token(email_verification.token)
            user = self.db.query(User).filter_by(email_verification_hash=hashed_token).first()

            # E-Mail verification is only allowed for unverified users
            if not user or user.status != UserStatus.UNVERIFIED:
                raise AttributeError()

            user.status = UserStatus.VERIFIED
            self.db.commit()
            self.db.refresh(user)

            return LoginResponseDto(access_token=self._create_access_token(user.email))
        except Exception as e:
            self.db.rollback()
            raise AttributeError()

    def login(self, email: str, password: str) -> LoginResponseDto:
        user = self.db.query(User).filter_by(email=email).first()

        # Only verified user can login
        if not user or not user.email or user.status not in {UserStatus.VERIFIED}:
            raise AttributeError()
        if not verify_password(password, user.password_hash):
            raise AttributeError()

        user.last_login = datetime.now().isoformat()
        self.db.commit()

        return LoginResponseDto(access_token=self._create_access_token(email=user.email))
    
    def forget_password(self, forget_password_dto: ForgetPasswordRequestDto):
        user = self.db.query(User).filter_by(email=forget_password_dto.email).first()

        if not user or not user.email or user.status not in {UserStatus.VERIFIED}:
            return None
        
        try:
            password_reset_token = generate_token()
            user.password_reset_hash = hash_token(password_reset_token)

            self.db.commit()
            self.db.refresh(user)
            return ForgetPasswordDto(email=user.email, password_token=password_reset_token)
        except Exception:
            self.db.rollback()
            return None
    
    def reset_password(self, reset_password_dto: ResetPasswordRequestDto):

        reset_password_hash = hash_token(reset_password_dto.token)
        user = self.db.query(User).filter_by(password_reset_hash=reset_password_hash).first()

        if not user:
            raise AttributeError()

        try:
            user.password_hash = hash_password(reset_password_dto.password)
            user.password_reset_hash = None

            self.db.commit()
        except Exception:
            self.db.rollback()
            raise AttributeError()

    def get_guests_of_user(self, user: User) -> GuestListDto:
        guestList = GuestListDto()
        for guest in user.associated_guests:
            status = not (guest.status == GuestStatus.EXCUSED)

            guestList.guests.append(GuestDto(id=guest.id, first_name=guest.first_name,
                                             roles=[role.name.value for role in guest.roles],
                                             last_name=guest.last_name, joins=status,
                                             food_option=guest.food_option.value,
                                             dessert_option=guest.dessert_option.value,
                                             allergies=guest.allergies,
                                             favorite_fairy_tale_character=guest.favorite_fairy_tale_character,
                                             favorite_tool=guest.favorite_tool))
        return guestList
    
    def guest_infos(self):
        guest_dto = []
        for guest in self.db.query(Guest).all():
            guest_dto.append(GuestDto(id=guest.id,
                                      first_name=guest.first_name,
                                      last_name=guest.last_name,
                                      joins=guest.status == GuestStatus.REGISTERED,
                                      food_option=guest.food_option.value,
                                      dessert_option=guest.dessert_option.value,
                                      allergies=guest.allergies,
                                      favorite_fairy_tale_character=guest.favorite_fairy_tale_character,
                                      favorite_tool=guest.favorite_tool))
        return GuestListDto(guests=guest_dto)

    def update_guests_of_user(self, guest_dtos: List[GuestDto], user: User) -> int:
        """ Updates preferences of 
        
        Guest roles are not updated

        Args:
            guest_dtos (List[GuestDto]): _description_
            user (User): _description_

        Raises:
            AttributeError: _description_
            AttributeError: _description_

        Returns:
            int: _description_
        """
        # Check if only guest associated with the logged in user are changed
        allowed_ids = set(associated_guest.id for associated_guest in user.associated_guests)
        received_ids = set(guest.id for guest in guest_dtos)

        if received_ids - allowed_ids:
            raise AttributeError()

        try:
            no_of_guests = 0
            for guest_dto in guest_dtos:
                guest = self.db.query(Guest).filter_by(id=guest_dto.id).first()

                guest.status = GuestStatus.REGISTERED if guest_dto.joins else GuestStatus.EXCUSED

                guest.food_option = FoodOption(guest_dto.food_option)
                guest.dessert_option = DessertOption(guest_dto.dessert_option)
                guest.allergies = guest_dto.allergies
                guest.favorite_fairy_tale_character = guest_dto.favorite_fairy_tale_character
                guest.favorite_tool = guest_dto.favorite_tool
                no_of_guests += 1

            self.db.commit()
            return no_of_guests
        except Exception as e:
            logging.error(f'Failed to register user {guest_dtos}. {e}')
            self.db.rollback()
            raise AttributeError()
    
    def get_contact_info(self) -> ContactListDto:
        target_roles = [GuestRole.ADMIN, GuestRole.WITNESS]
        guests = self.db.query(Guest)\
                .join(Role.guest).join(User).filter(Role.name.in_(target_roles), and_(User.email != None)).order_by(Guest.id).all()
        
        contacts = [ContactInfoDTO(id=g.id,
                                   first_name=g.first_name,
                                   last_name=g.last_name) for g in guests]
        return ContactListDto(contacts=contacts)
    
    def send_message(self, message: MessageDto):
        target_roles = [GuestRole.ADMIN, GuestRole.WITNESS]
        has_admin_role = self.db.query(Guest).join(Role.guest).filter(Role.name.in_(target_roles), and_(Guest.id==message.receiver_id)).first()

        if has_admin_role:
            user = self.db.query(User).join(Guest.user).filter(Guest.id==message.receiver_id, User.email != None).first()
        
        if not user:
            raise AttributeError()

        return {'email': user.email}


    def _create_access_token(self, email: str) -> str:
        data = {'sub': email}
        to_encode = data.copy()
        expires_delta = timedelta(minutes=self.config.api.access_token_expire_minutes)
        to_encode.update({'exp': datetime.utcnow() + expires_delta})
        encoded_jwt = jwt.encode(to_encode,
                                 key=self.config.api.secret_key,
                                 algorithm=self.config.api.algorithm)
        return encoded_jwt
