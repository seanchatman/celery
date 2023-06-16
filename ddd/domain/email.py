import os
from dataclasses import dataclass
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import html2text

from ddd.domain.json_mixin import JsonMixin


@dataclass
class Email(JsonMixin):
    id: str = ""
    to: str = ""
    from_: str = ""
    subject: str = ""
    body: str = ""
    message: Message = None
    sent: bool = False

    def __post_init__(self):
        if self.message:
            self.to = self.message['To']
            self.from_ = self.message['From']
            self.subject = self.message['Subject']
            self.body = self.extract_body(self.message)

    def to_mime_message(self):
        mime_message = MIMEMultipart()
        mime_message['From'] = os.getenv('MAIL_USERNAME')
        mime_message['To'] = self.to
        mime_message['Subject'] = self.subject
        mime_message.attach(MIMEText(self.body, 'plain'))
        return mime_message

    def as_string(self):
        return self.to_mime_message().as_string()

    def extract_body(cls, message):
        body = ""
        if message.is_multipart():
            for part in message.get_payload():
                content_type = part.get_content_type()
                if content_type.startswith('text/'):
                    body = part.get_payload(decode=True).decode('utf-8')
                    break
                elif content_type.startswith('multipart/'):
                    body = cls.extract_body(part)
                    if body:
                        break
        else:
            body = message.get_payload(decode=True).decode('utf-8')
        return html2text.html2text(body)

    @property
    def sender_name(self):
        return self.from_.split(':')[0]
