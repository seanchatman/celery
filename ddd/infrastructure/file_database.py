from __future__ import annotations

import os
import json

from ddd.domain.json_mixin import JsonMixin
from ddd.utils import get_project_root


class FileDatabase:
    def __init__(self, schema):
        self.filename = os.path.join(get_project_root(), schema.__qualname__.lower() + ".json")
        self.schema = schema

        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump([], f)

    def get(self, id) -> dict | None:
        with open(self.filename, "r") as f:
            data = json.load(f)

        for obj in data:
            if obj["id"] == id:
                return obj

        return None

    def save(self, obj: JsonMixin) -> None:
        with open(self.filename, "r") as f:
            data = json.load(f)

        for i, existing_obj in enumerate(data):
            if existing_obj["id"] == obj.id:
                data[i] = obj.to_dict()
                break
        else:
            data.append(obj.to_dict())

        with open(self.filename, "w") as fw:
            json.dump(data, fw)

    def delete(self, id) -> None:
        with open(self.filename, "r") as f:
            data = json.load(f)

        data = [obj for obj in data if obj.id != id]

        with open(self.filename, "w") as f:
            json.dump(data, f)

    def get_all(self) -> list[dict]:
        with open(self.filename, "r") as f:
            data = json.load(f)

        return data
