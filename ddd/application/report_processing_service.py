# report_processing_service.py
import os
import time

from celery.utils.log import get_task_logger
from dotenv import load_dotenv

from ddd.application.feedback_service import FeedbackService
from ddd.domain.email import Email
from ddd.domain.feedback import Feedback
from ddd.infrastructure.email_service import EmailService
from jinja2 import Template

from ddd.infrastructure.repositories import EmployeeRepository, FeedbackRepository

logger = get_task_logger(__name__)

def _generate_email_content(employees_without_reports, feedback_with_red_flags):
    template = Template("""\
Dear Manager,
{% if employees_without_reports %}
The following employees did not submit their reports today:
{% for employee in employees_without_reports %}
- {{ employee.email_addr }}
{% endfor %}
Please follow up with them to ensure they submit their reports in a timely manner.
{% endif %}
{% if feedback_with_red_flags %}
Reports with Red Flags:
{% for feedback in feedback_with_red_flags %}
{{ feedback.name }}:
{% for action_item in feedback.action_items %}
- {{ action_item }}
{% endfor %}
{% endfor %}
{% endif %}
Please review these reports and take appropriate action as needed.

Best regards,
Your Automated Report System
""")

    return template.render(
        employees_without_reports=employees_without_reports,
        feedback_with_red_flags=feedback_with_red_flags
    )


class ReportProcessingService:
    @staticmethod
    def gen_feedback(emails: list[Email]) -> list[Feedback]:
        return [FeedbackService().gen_feedback(email) for email in emails]

    @staticmethod
    def process_reports(feedbacks: list[Feedback]):
        logger.info("Processing reports...")
        employees = EmployeeRepository().get_all()

        for f in feedbacks:
            try:
                employee = next(e for e in employees if e.name == f.name)
                employee.report_submitted = True
            except StopIteration:
                pass

        employees_without_reports = [e for e in employees if not e.report_submitted]
        feedback_with_red_flags = [fb for fb in feedbacks if fb.has_red_flag]

        email_content = _generate_email_content(employees_without_reports, feedback_with_red_flags)

        # today's date
        today = time.strftime("%m/%d/%Y")
        mail = Email(
            to=os.getenv('TO'),
            subject=f"Daily Report ({today}) - Employees who did not submit reports and Reports with Red Flags",
            body=email_content
        )

        logger.info(f"Daily Report ({today})\n{email_content}")

        logger.info(f"Sending email to {mail.to}...")

        EmailService().send_email(mail)

        # Wait for 5 seconds to avoid rate limiting
        time.sleep(5)

        # os.getenv('CC') is a comma separated list of emails
        if os.getenv('CC'):
            cc = os.getenv('CC').split(',')
            for addr in cc:
                # Wait for 5 seconds to avoid rate limiting
                time.sleep(5)
                mail.to = addr
                logger.info(f"Sending email to {mail.to}...")
                EmailService().send_email(mail)

        EmailService().send_email(mail)


if __name__ == '__main__':
    load_dotenv('/Users/seanchatman/dev/celery/.env')

    ReportProcessingService.process_reports()
