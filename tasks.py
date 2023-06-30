import os
from celery import Celery
from celery.utils.log import get_task_logger
from dotenv import load_dotenv

from ddd.application.feedback_service import FeedbackService
from ddd.application.report_processing_service import ReportProcessingService
from celery.schedules import crontab

from ddd.infrastructure.email_service import EmailService

app = Celery('tasks', broker=os.getenv("CELERY_BROKER_URL"))
logger = get_task_logger(__name__)

if os.path.exists('/etc/secrets/.env'):
    load_dotenv(dotenv_path='/etc/secrets/.env')
else:
    load_dotenv()

@app.task
def check_email():
    logger.info("Checking email...")
    emails = EmailService().get_days_emails()

    feedbacks = FeedbackService().gen_feedbacks(emails)

    ReportProcessingService().process_reports(feedbacks)


app.conf.beat_schedule = {
    'daily-email': {
        'task': 'tasks.check_email',
        'schedule': crontab(hour=17, minute=0),
    }
}
