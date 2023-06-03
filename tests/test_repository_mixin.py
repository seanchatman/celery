import tempfile
import os
import pytest

from ddd.infrastructure import FileDatabase

from ddd.domain import Employee
from ddd.infrastructure.repositories import RepositoryMixin

alice = {'id': 'alice@test.com', 'email_addr': 'alice@test.com', 'name': 'Alice'}
bob = {'id': 'bob@test.com', 'email_addr': 'bob@test.com', 'name': 'Bob'}

alice = Employee(**alice)
bob = Employee(**bob)


class TestRepositoryMixin:
    @pytest.fixture
    def db(self):
        temp_dir = tempfile.TemporaryDirectory()
        db_path = os.path.join(temp_dir.name, 'test_db.csv')
        db = FileDatabase(db_path, Employee)
        yield db
        temp_dir.cleanup()

    def test_get_and_save(self, db):
        repo = RepositoryMixin(db)
        repo.save(alice)
        assert repo.get(alice.id).get('id') == alice.id

    def test_delete(self, db):
        repo = RepositoryMixin(db)
        repo.save(alice)
        repo.delete(alice.id)
        assert db.get(alice.id) is None

    def test_get_all(self, db):
        repo = RepositoryMixin(db)
        repo.save(alice)
        repo.save(bob)
        assert repo.get_all()[1].get('id') == bob.id
