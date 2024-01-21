import os

from app.src.email_sender import send_verification_email
from app.src.config.app_config import load_config
from tests.local_smtp_server import smtp_server


def test_send_verification_email(smtp_server):
    os.environ['APP_ENV'] = 'testing'
    config = load_config()
    token = '123'

    exp_url = f'{config.frontend_base_url}/email-verification?token={token}'

    prev_mail_count = smtp_server.handler.count_messages()

    send_verification_email('test@gmail.com', verification_token=token)

    assert smtp_server.handler.count_messages() == prev_mail_count + 1

    act_content = smtp_server.handler.get_latest_message().get_html_content()

    assert f'<a href="{exp_url}">' in act_content
