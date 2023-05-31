import os
import time

from celery import Celery
from celery.utils.log import get_task_logger
from flask import Flask, flash, render_template, redirect, request
from celery import Celery
from celery.utils.log import get_task_logger
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import email
from chat_agent import ChatAgent
import html2text
from celery.schedules import crontab
app = Celery('tasks', broker=os.getenv("CELERY_BROKER_URL"))
logger = get_task_logger(__name__)

if os.path.exists('/etc/secrets/.env'):
    load_dotenv(dotenv_path='/etc/secrets/.env')
else:
    load_dotenv()

@app.task
def check_email():
    logger.info("Checking email...")
    try:
        conn = imaplib.IMAP4_SSL('imap.gmail.com')
        conn.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))

        # Get a list of all new messages
        conn.select('INBOX')
        typ, data = conn.search(None, 'UNSEEN')

        # Iterate over all messages
        for num in data[0].split():
            typ, data = conn.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            subject = msg['Subject']
            # Get the body of the email
            body = html2text.html2text(str(msg.get_payload()[0]))

            # Only take the first 2000 characters
            body = body[:2000]

            agent = ChatAgent(system_prompt="""You are a COB Update Feedback AGI that utilizes natural language 
            processing and sentiment analysis to provide insightful feedback on end-of-day emails. Using 
            machine learning algorithms and historical data, the AGI identifies potential issues that may 
            impact employee morale, giving managers the opportunity to address concerns before they become 
            larger issues. By analyzing the patterns and language used in COB reports, the AGI can provide 
            targeted feedback to employees, identifying areas where more clarity is needed and offering 
            actionable suggestions for improvement. With its ability to provide real-time feedback and 
            analysis, the COB Update Feedback AGI is an invaluable tool for organizations looking to improve 
            transparency, communication, and overall employee morale.""")

            reply = agent.submit("Give recommendations on state of employee and if any mgr actions are needed "
                                 "based on the information provided. Give direct actionable answers. "
                                 "Response should be elegantly formatted with bullet points. "
                                 ":\n\n" +
                                 body)

            agent.clear()

            send_email.delay(os.getenv('To'), f"{subject} from {msg['From']}", reply)

            # Wait for 5 seconds to avoid rate limiting
            time.sleep(5)

            # os.getenv('CC') is a comma separated list of emails
            if os.getenv('CC'):
                cc = os.getenv('CC').split(',')
                for addr in cc:
                    # Wait for 5 seconds to avoid rate limiting
                    time.sleep(5)
                    send_email.delay(addr, f"{subject} from {msg['From']}", reply)
    except Exception as e:
        logger.info(str(e))
        return str(e)


@app.task
def send_email(to, subject, body):
    logger.info("Sending email...", subject, body)
    email_subject = subject
    email_message = body

    sender_email = os.getenv('MAIL_USERNAME')
    sender_password = os.getenv('MAIL_PASSWORD')

    message = MIMEMultipart()
    message['From'] = os.getenv('MAIL_USERNAME')
    message['To'] = to
    message['Subject'] = email_subject
    message.attach(MIMEText(email_message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)

    try:
        server.starttls()
        server.login(sender_email, sender_password)
        logger.info("Sending email to", to)
        server.sendmail(sender_email, to, message.as_string())
        server.quit()
        return "Your email(s) have been sent."
    except Exception as e:
        logger.info(str(e))
        return str(e)


app.conf.beat_schedule = {
    'check-email-every-5-seconds': {
        'task': 'tasks.check_email',
        'schedule': crontab(minute='*/1')
    }
}
