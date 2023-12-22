import os
from fastapi.testclient import TestClient

os.environ['APP_ENV'] = 'testing'

from src.routes.v1 import app_v1
from src.routes.dto import LoginData, RegistrationData, EmailVerificationDate

from tests.temporal_setup import setup_backend, setup_db
from tests.local_smtp_server import smtp_server


client = TestClient(app=app_v1)


def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {'message': 'pong'}


def test_if_wrong_user_inviation_token_is_rejected(setup_backend):
    data = RegistrationData(email='test@gmail.com', password='123', invitation_token='123')
    respone = client.post('/user-register', json=data.model_dump())
    assert respone.status_code == 401


def test_if_wrong_email_verification_token_is_rejected(setup_backend):
    data = EmailVerificationDate(token='123')
    response = client.post('/email-verification', json=data.model_dump())
    assert response.status_code == 401


def test_if_wrong_login_is_rejected(setup_backend):
    login_data = LoginData(email='test@gmail.com', password='123')
    response = client.post('/login', json=login_data.model_dump())
    assert response.status_code == 401


def test_if_guest_info_not_accessible_for_unauthenticated_users():
    response = client.get('/guest-info')
    assert response.status_code == 401

def test_if_user_can_register_with_valid_token(smtp_server, setup_backend):
    invitations = setup_backend

    guest0 = invitations[list(invitations.keys())[0]]
    invitation_token = guest0['token']
    exp_email = 'test@mail.com'

    client = TestClient(app=app_v1)

    # Simulate registration with email
    data = RegistrationData(email=exp_email, password='123', invitation_token=invitation_token)
    response = client.post('/user-register', json=data.model_dump())
    assert response.status_code == 200

    token = smtp_server.handler.get_latest_message().get_token()
    act_email = smtp_server.handler.get_latest_message().get_first_recipient()

    assert token is not None
    assert act_email == exp_email

    # Simulate verification of email
    data = EmailVerificationDate(token=token)
    response = client.post('/email-verification', json=data.model_dump())
    assert response.status_code == 200


def test_if_user_can_register_with_another_email_before_validation(smtp_server, setup_backend):
    invitations = setup_backend

    guest0 = invitations[list(invitations.keys())[0]]
    invitation_token = guest0['token']
    exp_email0 = 'wrong_email@mail.com'
    exp_email1 = 'correct_email@mail.com'

    client = TestClient(app=app_v1)

    # Simulate registration with a wrong email address (e.g. typo)
    data = RegistrationData(email=exp_email0, password='123', invitation_token=invitation_token)
    response = client.post('/user-register', json=data.model_dump())
    assert response.status_code == 200

    first_token = smtp_server.handler.get_latest_message().get_token()
    act_email = smtp_server.handler.get_latest_message().get_first_recipient()

    assert first_token is not None
    assert act_email == exp_email0

    # Simulate registration with another (correct) email address
    data = RegistrationData(email=exp_email1, password='123', invitation_token=invitation_token)
    response = client.post('/user-register', json=data.model_dump())
    assert response.status_code == 200

    second_token = smtp_server.handler.get_latest_message().get_token()
    act_email = smtp_server.handler.get_latest_message().get_first_recipient()

    assert second_token is not None
    assert act_email == exp_email1
    
    # Ensure token send to first email address (wrong) is no longer valid
    data = EmailVerificationDate(token=first_token)
    response = client.post('/email-verification', json=data.model_dump())
    assert response.status_code == 401

    # Ensure token send to second email address is no longer valid
    data = EmailVerificationDate(token=second_token)
    response = client.post('/email-verification', json=data.model_dump())
    assert response.status_code == 200


def test_if_user_cannot_register_with_another_email_after_verification(smtp_server, setup_backend):
    invitations = setup_backend

    guest0 = invitations[list(invitations.keys())[0]]
    invitation_token = guest0['token']
    exp_email0 = 'test@mail.com'
    exp_email1 = 'second_try@mail.com'

    client = TestClient(app=app_v1)

    # Simulate registration with email
    data = RegistrationData(email=exp_email0, password='123', invitation_token=invitation_token)
    response = client.post('/user-register', json=data.model_dump())
    assert response.status_code == 200

    token = smtp_server.handler.get_latest_message().get_token()
    act_email = smtp_server.handler.get_latest_message().get_first_recipient()

    assert token is not None
    assert act_email == exp_email0

    # Simulate verification of email
    data = EmailVerificationDate(token=token)
    response = client.post('/email-verification', json=data.model_dump())
    assert response.status_code == 200

    # Ensure registration with another email address is no longer possible
    data = RegistrationData(email=exp_email1, password='123', invitation_token=invitation_token)
    response = client.post('/user-register', json=data.model_dump())
    assert response.status_code == 401


def test_if_registered_user_can_login(smtp_server, setup_backend):
    invitations = setup_backend

    guest0 = invitations[list(invitations.keys())[0]]
    invitation_token = guest0['token']
    exp_email = 'test@mail.com'
    password = '123'

    client = TestClient(app=app_v1)

    # Simulate registration with email
    data = RegistrationData(email=exp_email, password=password, invitation_token=invitation_token)
    response = client.post('/user-register', json=data.model_dump())
    assert response.status_code == 200

    token = smtp_server.handler.get_latest_message().get_token()
    act_email = smtp_server.handler.get_latest_message().get_first_recipient()

    assert token is not None
    assert act_email == exp_email

    # Simulate verification of email
    data = EmailVerificationDate(token=token)
    response = client.post('/email-verification', json=data.model_dump())
    assert response.status_code == 200

    login_data = LoginData(email=exp_email, password=password)
    response = client.post('/login', json=login_data.model_dump())
    assert response.status_code == 200
    assert 'access_token' in response.json()

    token = response.json()['access_token']
    response = client.get('/guest-info', headers={'Authorization': f'Bearer {token}',
                                                  'Content-Type': 'application/json' })
    
    assert response.status_code == 200
