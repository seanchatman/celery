import imaplib
import smtplib
from datetime import datetime, timedelta

import pytz
from dotenv import load_dotenv
import os
import email

from ddd.domain.report import Report
from ddd.domain.email import Email
from ddd.domain.employee import Employee

smtp_server = 'smtp.gmail.com'
imap_server = 'imap.gmail.com'


class EmailService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            load_dotenv()

            cls._instance = super().__new__(cls)
            cls._instance.server = smtplib.SMTP(smtp_server, 587)
            cls._instance.conn = imaplib.IMAP4_SSL(imap_server)
        return cls._instance
    
    def send_email(self, message: Email):
        sender_email = os.getenv('MAIL_USERNAME')
        sender_password = os.getenv('MAIL_PASSWORD')

        self.server.connect(smtp_server, 587)
        self.server.starttls()
        self.server.login(sender_email, sender_password)
        self.server.sendmail(sender_email, message.to, message.as_string())
        message.sent = True
        self.server.quit()

    def connect_to_email_server(self):
        self.conn.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
        self.conn.select('INBOX')

    def disconnect_from_email_server(self):
        if self.conn:
            self.conn.logout()

    def get_days_emails(self) -> list[Email]:
        self.connect_to_email_server()

        utc_now = datetime.now(pytz.utc)
        time_delta = timedelta(days=1)
        utc_since = (utc_now - time_delta).strftime('%d-%b-%Y')
        utc_before = utc_now.strftime('%d-%b-%Y')

        _, data = self.conn.search(None, 'SINCE', utc_since, 'BEFORE', utc_before)
        email_ids = data[0].split()
        emails = []
        for email_id in email_ids:
            _, msg_data = self.conn.fetch(email_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            em = Email(message=msg)
            emails.append(em)

        self.disconnect_from_email_server()
        return emails

    @staticmethod
    def parse_emails(emails):
        reports = []
        for mail in emails:
            employee = Employee()
            subject = mail['Subject']
            body = Email.extract_body(mail)
            reports.append(Report(employee=employee, title=subject, content=body))
        return reports


