import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def send_verification_email(receiver_email: str, verification_token: str):
    # TODO: Use config to load email credentials
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    smtp_username = "nass3rver@gmail.com"
    smtp_password = ""

    sender_email = "noreplay@molitoris.org"
    subject = "Email Bestätigung"

    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = receiver_email

    # Path to the directory containing the template file
    template_dir = Path('./app/src/static/html')

    env = Environment(loader=FileSystemLoader(template_dir))

    template = env.get_template('email_verification_template.html')

    template_data = {
        'email_token': verification_token
    }

    email_content = template.render(template_data)

    # TODO: Use jinja2 to create email 
    text = f'{verification_token}'

    # Convert into MIMEText objects
    # Client tires to render last item first
    message.attach(MIMEText(text, 'plain'))
    message.attach(MIMEText(email_content, 'html'))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(host=smtp_server, port=smtp_port, context=context) as server:
        server.login(user=smtp_username, password=smtp_password)
        server.sendmail(from_addr=sender_email,
                        to_addrs=receiver_email, 
                        msg=message.as_string())