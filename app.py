"""WTF"""
import os
from flask import Flask, flash, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from celery.utils.log import get_task_logger
from datetime import datetime
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import email
from chat_agent import ChatAgent
import html2text
from celery.schedules import crontab

if os.path.exists('/etc/secrets/.env'):
    load_dotenv(dotenv_path='/etc/secrets/.env')
else:
    load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', "super-secret")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI',
                                                  "postgresql://postgres:postgres@localhost:5432/postgres")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

celery = Celery('tasks', broker=os.getenv("CELERY_BROKER_URL"))
logger = get_task_logger(__name__)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')


@celery.task
def add(x, y):
    logger.info(f'Adding {x} + {y}')
    return x + y

#
# class TimeModel(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#
#
# @celery.task
# def save_utc_datetime():
#     with app.app_context():
#         new_entry = TimeModel(created_at=datetime.utcnow())
#         db.session.add(new_entry)
#         db.session.commit()

@app.route("/")
def hello_world():
    # save_utc_datetime.delay()
    return render_template("main.html", title="Hello")


@app.route('/add', methods=['POST'])
def add_inputs():
    x = int(request.form['x'] or 0)
    y = int(request.form['y'] or 0)
    add.delay(x, y)
    flash("Your addition job has been submitted.")
    return redirect('/')


# @app.route('/email', methods=['POST'])
@celery.task
def check_email():
    print("Checking email...")
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
            # send_email(subject, reply)
            send_email.delay(f"{subject} from {msg['From']}", reply)
    except Exception as e:
        print(str(e))
        return str(e)


@celery.task
def send_email(subject, body):
    print("Sending email...", subject, body)
    email_subject = subject
    email_message = body

    sender_email = os.getenv('MAIL_USERNAME')
    sender_password = os.getenv('MAIL_PASSWORD')
    receiver_email = os.getenv('TO')

    message = MIMEMultipart()
    message['From'] = os.getenv('MAIL_USERNAME')
    message['To'] = os.getenv('TO')
    message['Cc'] = os.getenv('CC')
    message['Subject'] = email_subject
    message.attach(MIMEText(email_message, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()

        flash("Your email has been sent.")
        return redirect('/')
    except Exception as e:
        print(str(e))
        return str(e)


celery.conf.beat_schedule = {
    'check-email-every-5-seconds': {
        'task': 'app.check_email',
        'schedule': crontab(minute='*/5')
    },
}