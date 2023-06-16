# report_processing_service.py
import os
import time

from dotenv import load_dotenv

from ddd.application.feedback_service import FeedbackService
from ddd.domain.email import Email
from ddd.domain.feedback import Feedback
from ddd.infrastructure.email_service import EmailService
from jinja2 import Template

from ddd.infrastructure.repositories import EmployeeRepository, FeedbackRepository


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
{{ feedback.content }}:
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
    def gen_feedback(self, emails: list[Email]) -> list[Feedback]:
        return [FeedbackService().gen_feedback(email.body) for email in emails]

    def process_reports(self):
        for f in FeedbackRepository().get_all():
            employee = EmployeeRepository().get(f.name)
            employee.report_submitted = True
            EmployeeRepository().save(employee)

        employees_without_reports = [e for e in EmployeeRepository().get_all() if not e.report_submitted]
        feedback_with_red_flags = [fb for fb in FeedbackRepository().get_all() if fb.has_red_flags()]


        email_content = _generate_email_content(employees_without_reports, feedback_with_red_flags)

        mail = Email(
            to=os.getenv('TO'),
            subject="Daily Report - Employees who did not submit reports and Reports with Red Flags",
            body=email_content
        )

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
                EmailService().send_email(mail)

        EmailService().send_email(mail)


if __name__ == '__main__':
    load_dotenv('/Users/seanchatman/dev/celery/.env')

    ReportProcessingService().process_reports()
