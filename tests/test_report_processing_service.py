from unittest.mock import MagicMock

import pytest

from ddd.application.feedback_service import FeedbackService
from ddd.application.report_processing_service import _generate_email_content
from ddd.domain.email import Email
from ddd.domain.feedback import Feedback


class TestReportProcessingService:
    @pytest.fixture
    def employee_repo(self):
        with MagicMock() as mock:
            yield mock

    @pytest.fixture
    def feedback_repo(self):
        with MagicMock() as mock:
            yield mock

    @pytest.fixture
    def email_service(self):
        with MagicMock() as mock:
            yield mock

    @pytest.fixture
    def feedback_service(self):
        return FeedbackService()

    @pytest.fixture
    def email(self):
        return Email('manager@test.com', 'subject', 'body')

    def test_generate_email_content_no_data(self):
        employees_without_reports = []
        feedback_with_red_flags = []

        expected_output = """\
Dear Manager,

"""

        assert _generate_email_content(employees_without_reports, feedback_with_red_flags) == expected_output

    def test_generate_email_content_employees_without_reports(self):
        employees_without_reports = [
            MagicMock(email_addr='alice@test.com'),
            MagicMock(email_addr='bob@test.com'),
        ]
        feedback_with_red_flags = []

        expected_output = """\
Dear Manager,

The following employees did not submit their reports today:

- alice@test.com
- bob@test.com

Please follow up with them to ensure they submit their reports in a timely manner.

"""

        assert _generate_email_content(employees_without_reports, feedback_with_red_flags) == expected_output

    def test_generate_email_content_feedback_with_red_flags(self):
        employees_without_reports = []
        feedback_with_red_flags = [
            MagicMock(employee_id='alice@test.com', feedback='feedback 1', red_flags=2),
            MagicMock(employee_id='bob@test.com', feedback='feedback 2', red_flags=1),
        ]

        expected_output = """\
Dear Manager,

Reports with Red Flags:

- Employee ID: alice@test.com
  Feedback: feedback 1
  Red Flags: 2

- Employee ID: bob@test.com
  Feedback: feedback 2
  Red Flags: 1

"""

        assert _generate_email_content(employees_without_reports, feedback_with_red_flags) == expected_output

    def test_feedback_service_get_feedback_with_red_flags(self, feedback_service, feedback_repo):
        feedback_repo.get_all.return_value = [
            Feedback('alice', 'alice@test.com', 'feedback 1'),
            Feedback('bob', 'bob@test.com', 'feedback 2'),
            Feedback('charlie@test.com', 'feedback 3'),
        ]

        assert feedback_service.get_feedback_with_red_flags() == [
            Feedback('alice', 'alice@test.com', 'feedback 1'),
            Feedback('bob', 'bob@test.com', 'feedback 2'),
        ]

    def test_feedback_service_get_employees_without_reports(self, feedback_service, employee_repo):
        employee_repo.get_all.return_value = [
            MagicMock(email_addr='alice@test.com'),
            MagicMock(email_addr='bob@test.com'),
            MagicMock(email_addr='charlie@test.com'),
        ]
        feedback_service.get_feedback_with_red_flags.return_value = [
            Feedback('alice', 'alice@test.com', 'feedback 1'),
            Feedback('bob', 'bob@test.com', 'feedback 2'),
        ]

        assert feedback_service.get_employees_without_reports() == [
            MagicMock(email_addr='charlie@test.com'),
        ]

    def test_email_service_send_email(self, email_service, email):
        email_service.send_email(email)

        email_service.send_email.assert_called_once_with(email)