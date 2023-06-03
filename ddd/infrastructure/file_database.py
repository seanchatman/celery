import csv
import os

from ddd.utils import get_project_root


class FileDatabase:
    def __init__(self, schema):
        self.filename = os.path.join(get_project_root(), schema.__qualname__.lower() + ".csv")
        self.schema = schema
        self.fieldnames = list(schema.__annotations__.keys())
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(self.fieldnames)

    def get(self, id) -> dict | None:
        with open(self.filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('id') == id:
                    return row
        return None

    def save(self, obj) -> None:
        with open(self.filename, 'a') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(vars(obj))

    def delete(self, id) -> None:
        data = self.get_all()
        data = [x for x in data if x.get('id') != id]
        with open(self.filename, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(data)

    def get_all(self) -> list[dict]:
        with open(self.filename, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)
