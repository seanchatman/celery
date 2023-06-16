import os
from flask import Flask, flash, render_template, redirect, request, send_from_directory
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
from flask_cors import CORS

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


app = Flask(__name__, static_folder='react-app/build')
CORS(app)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(f"{app.static_folder}/{path}"):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
