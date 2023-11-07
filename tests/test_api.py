import os
import sys
from pytest import fixture
from fastapi.testclient import TestClient

sys.path.append('/workspaces/wedding-api/app')

from src.routes.v1 import app_v1
from src.routes.dto import LoginData, RegistrationData, EmailVerificationDate

client = TestClient(app=app_v1)

def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {'message': 'pong'}

def test_if_wrong_user_inviation_token_is_rejected():
    data = RegistrationData(email='test@gmail.com', password='123', invitation_token='123')
    respone = client.post('/user-register', json=data.model_dump())
    assert respone.status_code == 401

def test_if_wrong_email_verification_token_is_rejected():
    data = EmailVerificationDate(token='123')
    response = client.post('/email-verification', json=data.model_dump())
    assert response.status_code == 401

def test_if_wrong_login_is_rejected():
    login_data = LoginData(email='test@gmail.com', password='123')
    response = client.post('/login', json=login_data.model_dump())
    assert response.status_code == 401

def test_if_guest_info_not_accessible_for_unauthenticated_users():
    response = client.get('/guest-info')
    assert response.status_code == 401
