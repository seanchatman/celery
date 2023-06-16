from dataclasses import dataclass
from datetime import datetime

from ddd.domain.employee import Employee
from ddd.domain.feedback import Feedback
from ddd.domain.json_mixin import JsonMixin


@dataclass
class Report(JsonMixin):
    id: str = ""
    employee: Employee = None
    feedback: Feedback = None
    title: str = ""
    content: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
