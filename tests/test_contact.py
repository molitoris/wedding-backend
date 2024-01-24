from tests.register_admin import setup_register
from tests.temporal_setup import setup_backend, setup_db
from tests.local_smtp_server import smtp_server

from src.routes.dto import LoginData, MessageDto

def test_get_contacts(setup_register):
    client, user_accounts, smtp_server = setup_register

    user_1 = user_accounts[0]

    data = LoginData(email=user_1.email, password=user_1.password)
    response = client.post('/login', json=data.model_dump())

    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}', 
               'Content-Type': 'application/json' } 
    
    response = client.get('/contact_info', headers=headers)

    for contact in response.json()['contacts']:
        id = contact['id']
        data = MessageDto(receiver_id=id,
                          subject='A simple question to answer',
                          message='I have a question about your website',
                          sender_email='example@test.org',
                          sender_phone='001 234 567 89')

        response = client.post('/send_message', json=data.model_dump())

        message = smtp_server.handler.get_latest_message().get_html_content()

        assert data.subject in message
        assert data.message in message
        assert data.sender_email in message
        assert data.sender_phone in message