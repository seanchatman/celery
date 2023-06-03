# domain.py
import os
import html2text

from dataclasses import dataclass
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import Message

@dataclass
class Employee:
    id: str = ""
    email_addr: str = ""
    name: str = ""
    report_submitted: str = "False"

    def did_not_submit_report(self):
        # This method checks if the employee did not submit a report
        return self.report_submitted == "False"


@dataclass
class Feedback:
    id: str = ""
    name: str = ""
    content: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()

    def has_red_flags(self) -> bool:
        return "<<RED_FLAG>>" in self.content


@dataclass
class Email:
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


@dataclass
class Report:
    id: str = ""
    employee: Employee = None
    feedback: Feedback = None
    title: str = ""
    content: str = ""
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
