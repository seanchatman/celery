from dataclasses import dataclass

from ddd.domain.json_mixin import JsonMixin


@dataclass
class Employee(JsonMixin):
    id: str = ""
    email_addr: str = ""
    name: str = ""
    report_submitted: str = "False"
