from __future__ import annotations

from ddd.domain.email import Email
from ddd.domain.report import Report
from ddd.domain.feedback import Feedback
from ddd.domain.employee import Employee
from ddd.infrastructure.file_database import FileDatabase


class RepositoryMixin:
    def __init__(self, db):
        self.db = db

    def get(self, id) -> dict:
        return self.db.get(id)

    def save(self, obj) -> None:
        self.db.save(obj)

    def delete(self, obj) -> None:
        self.db.delete(obj)

    def get_all(self) -> list[dict]:
        return self.db.get_all()

    def save_all(self, objs: list[object]) -> None:
        [self.save(obj) for obj in objs]

    def update(self, obj) -> None:
        self.db.update(obj)


class ReportRepository(RepositoryMixin):
    def __init__(self):
        super().__init__(FileDatabase(Report))

    def get(self, id) -> Report | None:
        return Report(**super().get(id))

    def get_all(self) -> list[Report]:
        return [Report(**x) for x in super().get_all()]


class FeedbackRepository(RepositoryMixin):
    def __init__(self):
        super().__init__(FileDatabase(Feedback))

    def get(self, id) -> Feedback | None:
        return Feedback(**super().get(id))

    def get_all(self) -> list[Feedback]:
        return [Feedback(**x) for x in super().get_all()]


class EmployeeRepository(RepositoryMixin):
    def __init__(self):
        super().__init__(FileDatabase(Employee))

    def get(self, id) -> Employee | None:
        return Employee(**super().get(id))

    def get_all(self) -> list[Employee]:
        return [Employee(**x) for x in super().get_all()]


class EmailRepository(RepositoryMixin):
    def __init__(self):
        super().__init__(FileDatabase(Email))

    def get(self, id) -> Email | None:
        return Email(**super().get(id))

    def get_all(self) -> list[Email]:
        return [Email(**x) for x in super().get_all()]
