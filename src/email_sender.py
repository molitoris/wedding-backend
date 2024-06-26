import smtplib
import ssl
from typing import Dict, List, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from src.config.app_config import load_config
from src.routes.dto import Message, ForgetPasswordDto


def send_password_reset_email(forget_password_dto: ForgetPasswordDto):
    config = load_config()

    subject = "Hochzeit Melanie & Rafael - Passwort Reset"
    template_name = 'email_password_reset.html'
    template_data = {
        'base_url': config.frontend_base_url,
        'password_token': forget_password_dto.password_token
    }

    plain_text = f'{forget_password_dto.password_token}'

    _send_email(receiver_email=forget_password_dto.email,
                subject=subject,
                plain_text=plain_text,
                template_name=template_name,
                template_data=template_data)


def send_message_email(receiver_email: str, message: Message):

    subject = 'Hochzeit Melanie & Rafael - Kontakt'
    template_name = 'email_contact_message_template.html'
    template_data = {
        'subject': message.subject,
        'message': message.message,
        'sender_email': message.sender_email,
        'sender_phone': message.sender_phone
    }
    plain_text = ''

    _send_email(receiver_email=receiver_email,
                subject=subject,
                plain_text=plain_text,
                template_name=template_name,
                template_data=template_data)


def send_verification_email(receiver_email: str, verification_token: str):

    config = load_config()

    subject = 'Hochzeit Melanie & Rafael - Email Bestätigung'

    template_data = {
        'base_url': config.frontend_base_url,
        'email_token': verification_token
    }

    _send_email(receiver_email=receiver_email,
                subject=subject,
                plain_text=f'{verification_token}',
                template_name='email_verification_template.html',
                template_data=template_data)


def send_reminer_email(guests: List[Tuple[str, str]], receiver_email: str):

    subject = 'Hochzeit Melanie & Rafael - Bald ist es soweit'

    greetings = ''
    for gender, name in guests:
        if gender == 'male':
            greetings += 'Lieber ' + name + ', '
        else:
            greetings += 'Liebe ' + name + ', '

    greetings = greetings.strip().strip(',')

    template_data = {
        'guest_count': len(guests),
        'greeting': greetings,
    }

    _send_email(receiver_email=receiver_email,
                subject=subject,
                plain_text='',
                template_name='email_reminder_template.html',
                template_data=template_data)


def _send_email(receiver_email: str,
                subject: str,
                plain_text: str,
                template_name: str,
                template_data: Dict,
                template_dir: Path = Path('./src/static/html')
                ):

    config = load_config()

    sender_email = 'noreplay@molitoris.org'

    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = receiver_email

    env = Environment(loader=FileSystemLoader(template_dir))

    template = env.get_template(template_name)

    email_content = template.render(template_data)

    # Convert into MIMEText objects
    # Client tires to render last item first
    message.attach(MIMEText(plain_text, 'plain'))
    message.attach(MIMEText(email_content, 'html'))

    context = ssl.create_default_context()
    with smtplib.SMTP(host=config.email.smtp_server, port=config.email.smtp_port) as server:

        # Running localhost does not require TLS
        if config.email.smtp_server != 'localhost':
            server.starttls(context=context)
            server.login(user=config.email.smtp_username, password=config.email.smtp_password)

        server.sendmail(from_addr=sender_email,
                        to_addrs=receiver_email,
                        msg=message.as_string())
