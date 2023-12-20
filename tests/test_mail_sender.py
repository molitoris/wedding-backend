import os
import sys
from email import message_from_bytes

sys.path.append('/workspaces/wedding-api/app')
sys.path.append('/workspaces/wedding-api/tests')

from app.src.email_sender import send_verification_email
from app.src.config.app_config import load_config
from tests.local_smtp_server import smtp_server


def get_html_from_email(content):
    msg = message_from_bytes(content)
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            # Look for plain text content
            if content_type == 'text/html':
                return part.get_payload(decode=True).decode(part.get_content_charset())

def test_send_verification_email(smtp_server):
    os.environ['APP_ENV'] = 'testing'
    config = load_config()
    token = '123'

    exp_url = f'{config.frontend_base_url}/email-verification?token={token}'

    send_verification_email('test@gmail.com', verification_token=token)

    assert len(smtp_server.handler.received_messages) == 1

    act_content = get_html_from_email(smtp_server.handler.received_messages[0][1])
    
    assert f'<a href="https://{exp_url}">' in act_content
