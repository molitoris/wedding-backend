import os

from unittest.mock import MagicMock
import pytest

from src.business_logic.services import Service
from src.database.db_tables import User, Guest, Role
from src.database.models.guest_role import GuestRole
from src.database.models.food_options import FoodOption
from src.database.models.dessert_options import DessertOption
from src.database.models.user_status import UserStatus
from src.database.models.guest_status import GuestStatus
from src.config.app_config import load_config
from src.routes.dto import RegistrationData, EmailVerificationDate, GuestDto
from src.security import hash_token, verify_password, generate_token


@pytest.fixture
def mock_db():
    db = MagicMock()
    query = MagicMock()
    result = MagicMock()
    result.first.return_value = None
    query.filter_by.return_value = result
    db.query.return_value = query

    return db, query, result


@pytest.mark.parametrize('status', [UserStatus.UNSEEN, UserStatus.UNVERIFIED])
def test_if_user_can_registration_with_valid_token(status, mock_db):
    os.environ['APP_ENV'] = 'testing'
    config = load_config()

    token = generate_token()
    hashed_token = hash_token(token)
    data = RegistrationData(invitation_token=token, email='test@mail.com', password='123')

    db_user = User()
    db_user.status = status
    db_user.invitation_hash = hash_token

    db, query, result = mock_db
    result.first.return_value = db_user

    s = Service(db=db, config=config)
    user, email_token = s.register_user(registration_data=data)

    query.filter_by.assert_called_once_with(invitation_hash=hashed_token)

    assert user.status == UserStatus.UNVERIFIED
    assert user.email == data.email
    assert user.email_verification_hash == hash_token(email_token)
    assert verify_password(data.password, user.password_hash)


@pytest.mark.parametrize('status', [UserStatus.DELETED, UserStatus.DISABLED, UserStatus.VERIFIED])
def test_if_user_cannot_registration_in_invalid_state(status, mock_db):
    os.environ['APP_ENV'] = 'testing'
    config = load_config()

    data = RegistrationData(invitation_token=generate_token(),
                            email='test@mail.com', password='123')

    db_user = User()
    db_user.status = status

    db, _, result = mock_db
    result.first.return_value = db_user

    s = Service(db=db, config=config)

    with pytest.raises(AttributeError):
        s.register_user(registration_data=data)


@pytest.mark.parametrize('status', [UserStatus.UNSEEN])
def test_if_db_is_rolled_back_upon_error(status, mock_db):
    os.environ['APP_ENV'] = 'testing'
    config = load_config()

    data = RegistrationData(invitation_token=generate_token(),
                            email='test@mail.com', password='123')

    db_user = User()
    db_user.status = status

    db, _, result = mock_db
    result.first.return_value = db_user

    s = Service(db=db, config=config)

    db.commit.side_effect = Exception()

    with pytest.raises(AttributeError):
        s.register_user(registration_data=data)


@pytest.mark.parametrize('status', [UserStatus.UNVERIFIED])
def test_if_can_verify_email(status, mock_db):
    os.environ['APP_ENV'] = 'testing'
    config = load_config()

    token = generate_token()
    data = EmailVerificationDate(token=token)

    db_user = User()
    db_user.status = status

    db, query, result = mock_db
    result.first.return_value = db_user

    s = Service(db=db, config=config)

    s.verify_email(email_verification=data)

    query.filter_by.assert_called_once_with(email_verification_hash=hash_token(token))

    assert db_user.status == UserStatus.VERIFIED


@pytest.mark.parametrize('status', [UserStatus.DELETED, UserStatus.VERIFIED,
                                    UserStatus.DISABLED, UserStatus.UNSEEN])
def test_if_verify_email_handles_incorrect_states(status, mock_db):
    os.environ['APP_ENV'] = 'testing'
    config = load_config()

    token = generate_token()
    data = EmailVerificationDate(token=token)

    db_user = User()
    db_user.status = status

    db, query, result = mock_db
    result.first.return_value = db_user

    s = Service(db=db, config=config)

    with pytest.raises(AttributeError):
        s.verify_email(email_verification=data)


def test_if_can_get_initial_guest_of_user(mock_db):
    os.environ['APP_ENV'] = 'testing'
    config = load_config()

    g1 = Guest()
    g1.id = 0
    g1.first_name = ''
    g1.last_name = ''
    g1.roles = [Role(name=GuestRole.GUEST)]
    g1.food_option = FoodOption.UNDEFINED
    g1.dessert_option = DessertOption.UNDEFINED
    g1.allergies = ''
    g1.status = GuestStatus.UNDEFINED
    g1.favorite_fairy_tale_character = ''
    g1.favorite_tool = ''

    db_user = User()
    db_user.associated_guests = [g1]

    db, _, _ = mock_db

    s = Service(db=db, config=config)

    response = s.get_guests_of_user(db_user)

    assert len(db_user.associated_guests) == len(response.guests)
    assert response.guests[0].joins == True
    assert response.guests[0].allergies == g1.allergies
    assert response.guests[0].food_option == g1.food_option.value


def test_if_can_update_initial_guest_of_user(mock_db):
    os.environ['APP_ENV'] = 'testing'
    config = load_config()

    g1 = Guest()
    g1.id = 0
    g1.first_name = ''
    g1.last_name = ''
    g1.roles = []
    g1.food_option = FoodOption.UNDEFINED
    g1.dessert_option = DessertOption.UNDEFINED
    g1.allergies = ''
    g1.status = GuestStatus.UNDEFINED
    g1.favorite_fairy_tale_character = ''
    g1.favorite_tool = ''

    guest_dto = GuestDto(id=g1.id,
                         first_name='', last_name='',
                         roles=[GuestRole.GUEST.value],
                         joins=True, 
                         food_option=FoodOption.VEGETARIAN.value,
                         dessert_option=DessertOption.CHEESE.value,
                         allergies='Crustaceans', 
                         favorite_fairy_tale_character='Cinderella', 
                         favorite_tool='hammer')

    db_user = User()
    db_user.associated_guests = [g1]

    db, _, result = mock_db
    result.first.return_value = g1

    s = Service(db=db, config=config)

    s.update_guests_of_user(guest_dtos=[guest_dto], user=db_user)

    assert g1.roles == []  # Roles are not updated
    assert g1.food_option == FoodOption.VEGETARIAN
    assert g1.dessert_option == DessertOption.CHEESE
    assert g1.favorite_fairy_tale_character == guest_dto.favorite_fairy_tale_character
    assert g1.favorite_tool == guest_dto.favorite_tool
    
    response = s.get_guests_of_user(db_user)

    assert len(db_user.associated_guests) == len(response.guests)
    assert response.guests[0].joins == True
    assert response.guests[0].allergies == g1.allergies
    assert response.guests[0].food_option == g1.food_option.value
