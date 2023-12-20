import pytest

from aiosmtpd.controller import Controller

class TestSmtpHandler():
    received_messages = []

    async def handle_DATA(self, server, session, envelope):
        self.received_messages.append((envelope.mail_from, envelope.content))
        return '250 OK'
    

@pytest.fixture(scope='module')
def smtp_server():
    handler = TestSmtpHandler()
    server = Controller(handler, hostname='127.0.0.1', port=1025)

    server.start()
    print("Server started. Press Return to quit.")

    yield server

    server.stop()