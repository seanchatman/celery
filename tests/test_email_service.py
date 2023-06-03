"""
import csv
import imaplib
import smtplib
from datetime import datetime, timedelta

from dotenv import load_dotenv
import os
import email_addr
import html2text

from ddd.domain import Report, Employee, Email, Feedback


class EmailService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            load_dotenv()
            smtp_server = 'smtp.gmail.com'
            imap_server = 'imap.gmail.com'
            cls._instance = super().__new__(cls)
            cls._instance.server = smtplib.SMTP(smtp_server, 587)
            cls._instance.conn = imaplib.IMAP4_SSL(imap_server)
        return cls._instance
    
    def send_email(self, message: Email):
        sender_email = os.getenv('MAIL_USERNAME')
        sender_password = os.getenv('MAIL_PASSWORD')

        self.server.starttls()
        self.server.login(sender_email, sender_password)
        self.server.sendmail(sender_email, message.to, message.as_string())
        self.server.quit()

    def connect_to_email_server(self):
        self.conn.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
        self.conn.select('INBOX')

    def disconnect_from_email_server(self):
        if self.conn:
            self.conn.logout()

    def get_days_emails(self):
        self.connect_to_email_server()
        # _, data = self.conn.search(None, 'UNSEEN')
        # Search for all emails received today
        now = datetime.now()
        since = (now - timedelta(days=1)).strftime('%d-%b-%Y')
        before = now.strftime('%d-%b-%Y')

        _, data = self.conn.search(None, 'SINCE', since, 'BEFORE', before)
        email_ids = data[0].split()
        emails = []
        for email_id in email_ids:
            _, msg_data = self.conn.fetch(email_id, '(RFC822)')
            msg = email_addr.message_from_bytes(msg_data[0][1])
            emails.append(msg)
        self.disconnect_from_email_server()
        return emails

    def parse_emails(self, emails):
        reports = []
        for mail in emails:
            employee = Employee()
            subject = mail['Subject']
            body = self.extract_email_body(mail)
            reports.append(Report(employee=employee, title=subject, content=body))
        return reports

    def extract_email_body(self, mail):
        body = ""
        if mail.is_multipart():
            for part in mail.get_payload():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode('utf-8')
        else:
            body = mail.get_payload(decode=True).decode('utf-8')
        return html2text.html2text(body)
"""
import os
import pytest
from unittest.mock import Mock, patch

from ddd.infrastructure.email_service import EmailService
from ddd.domain import Email


class TestEmailService:

    @patch('smtplib.SMTP', autospec=True)
    def test_send_email(self, mock_smtp):
        message = Email(
            to='test@example.com',
            subject='Test Email',
            body='This is a test email_addr'
        )
        EmailService().send_email(message)
        assert mock_smtp.called
        assert message.sent is True

    @patch('imaplib.IMAP4_SSL', autospec=True)
    def test_connect_to_email_server(self, mock_imap):
        EmailService().connect_to_email_server()
        assert mock_imap.called

    @patch('imaplib.IMAP4_SSL', autospec=True)
    def test_disconnect_from_email_server(self, mock_imap):
        EmailService().disconnect_from_email_server()
        assert mock_imap.called

    def test_get_unseen_emails(self, email_service):
        # Add some test emails to the mailbox
        EmailService().send_email(Email(to='test@example.com', subject='Test Email 1'))
        EmailService().send_email(Email(to='test@example.com', subject='Test Email 2'))
        EmailService().send_email(Email(to='test@example.com', subject='Test Email 3'))
        # Get the unseen emails
        emails = email_service.get_days_emails()
        # Check that the correct number of emails were returned
        assert len(emails) == 3
        # Check that the emails have the correct subject lines
        assert emails[0]['Subject'] == 'Test Email 1'
        assert emails[1]['Subject'] == 'Test Email 2'
        assert emails[2]['Subject'] == 'Test Email 3'