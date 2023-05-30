"""WTF"""
import os
from flask import Flask, flash, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from celery.utils.log import get_task_logger
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', "super-secret")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_URI',
                                                  "postgresql://postgres:postgres@localhost:5432/postgres")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

celery = Celery('tasks', broker=os.getenv("CELERY_BROKER_URL"))
logger = get_task_logger(__name__)


@celery.task
def add(x, y):
    logger.info(f'Adding {x} + {y}')
    return x + y


@celery.task
def save_utc_datetime():
    with app.app_context():
        new_entry = TimeModel(created_at=datetime.utcnow())
        db.session.add(new_entry)
        db.session.commit()

@app.route("/")
def hello_world():
    save_utc_datetime.delay()
    return render_template("index.html", title="Hello")

class TimeModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/add', methods=['POST'])
def add_inputs():
    x = int(request.form['x'] or 0)
    y = int(request.form['y'] or 0)
    add.delay(x, y)
    flash("Your addition job has been submitted.")
    return redirect('/')

