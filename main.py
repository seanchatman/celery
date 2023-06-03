from ddd.application.feedback_service import FeedbackService
from ddd.application.report_processing_service import ReportProcessingService
from ddd.domain import Employee
from ddd.infrastructure.email_service import EmailService
from ddd.infrastructure.repositories import EmployeeRepository, FeedbackRepository

if __name__ == '__main__':
    # emails = EmailService().get_days_emails()

    # emails[0].body += "\n1 person quit"
    # feedbacks = FeedbackService().gen_feedbacks(emails)
    # FeedbackRepository().save_all(feedbacks)

    ReportProcessingService().process_reports()
    print('Done')
