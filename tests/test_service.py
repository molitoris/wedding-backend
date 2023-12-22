import os

from unittest.mock import MagicMock
import pytest

from src.business_logic.services import Service
from src.database.db_tables import User
from src.database.models.user_status import UserStatus
from src.config.app_config import load_config
from src.routes.dto import RegistrationData, EmailVerificationDate
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
