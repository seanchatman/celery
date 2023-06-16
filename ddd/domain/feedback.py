from dataclasses import dataclass
from datetime import datetime

from ddd.domain.json_mixin import JsonMixin


@dataclass
class Feedback(JsonMixin):
    id: str = ""
    name: str = ""
    content: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()

    def has_red_flags(self) -> bool:
        return "<<RED_FLAG>>" in self.content
