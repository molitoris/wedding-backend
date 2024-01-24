import os
import random
import string

import pytest
from fastapi.testclient import TestClient

os.environ['APP_ENV'] = 'testing'

from src.routes.v1 import app_v1
from src.routes.dto import LoginData, RegistrationData, EmailVerificationDate

from tests.temporal_setup import setup_backend, setup_db
from tests.local_smtp_server import smtp_server

class UserData:

    def __init__(self, email: str, password: str) -> None:
        self.email = email
        self.password = password

def register_and_verify(client, smtp_server, token: str, email: str, password: str):
    data = RegistrationData(email=email, password=password, invitation_token=token)
    response = client.post('/user-register', json=data.model_dump())
    assert response.status_code == 200

    token = smtp_server.handler.get_latest_message().get_token()
    act_email = smtp_server.handler.get_latest_message().get_first_recipient()

    assert token is not None
    assert act_email == email

    # Simulate verification of email
    data = EmailVerificationDate(token=token)
    response = client.post('/email-verification', json=data.model_dump())
    assert response.status_code == 200

def pseudo_random_password(length: int = 6):
    return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=length))

def pseudo_random_email(provider: str ='@mail.com', length: int = 5):
    return ''.join(random.choices(string.ascii_lowercase, k=length)) + provider


@pytest.fixture
def setup_register(smtp_server, setup_backend):
    invitations = setup_backend

    client = TestClient(app=app_v1)

    user_accounts = []

    for key in invitations.keys():
        guest = invitations[key]
        invitation_token = guest['token']

        userdata = UserData(email=pseudo_random_email(),
                            password=pseudo_random_password())

        register_and_verify(client=client,
                            smtp_server=smtp_server,
                            token=invitation_token,
                            email=userdata.email,
                            password=userdata.password)
        
        user_accounts.append(userdata)

    return client, user_accounts, smtp_server