import pytest
import re
from typing import List, Optional
from email import message_from_bytes

from aiosmtpd.controller import Controller


class EMail:

    def __init__(self, envelope) -> None:
        self.envelope = envelope
    
    def get_sender(self) -> str:
        return self.envelope.mail_from
    
    def get_first_recipient(self) -> str:
        return self.envelope.rcpt_tos[0]
    
    def get_html_content(self) -> str:
        msg = message_from_bytes(self.envelope.content)
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/html':
                    return part.get_payload(decode=True).decode(part.get_content_charset())

    def get_token(self) -> Optional[str]:
        html_content = self.get_html_content()
    
        pattern = re.compile(r'email-verification\?token=(?P<token>\w+)\">')
        matches = re.search(pattern, html_content)
    
        if matches is None:
            return None
        
        return matches.group('token')


class TestSmtpHandler():
    received_messages: List[EMail] = []

    async def handle_DATA(self, server, session, envelope) -> str:
        self.received_messages.append(EMail(envelope))
        return '250 OK'
    
    def count_messages(self) -> int:
        return len(self.received_messages)
    
    def get_latest_message(self) -> EMail:
        return self.received_messages[-1]


@pytest.fixture
def smtp_server():
    handler = TestSmtpHandler()
    server = Controller(handler, hostname='127.0.0.1', port=1025)

    server.start()
    print("Server started. Press Return to quit.")

    yield server

    server.stop()
