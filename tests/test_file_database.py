import tempfile
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

from ddd.domain import Employee
from ddd.infrastructure.file_database import FileDatabase

alice = Employee(id='alice@test.com', email_addr='alice@test.com', name='Alice')
bob = Employee(id='bob@test.com', email_addr='bob@test.com', name='Bob')


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_get_project_root(temp_dir):
    with MagicMock() as mock:
        mock.return_value = temp_dir
        yield mock


@pytest.fixture
def db(mock_get_project_root):
    with patch('ddd.infrastructure.file_database.get_project_root', mock_get_project_root):
        db = FileDatabase(Employee)
        yield db


def test_create(db):
    assert len(db.get_all()) == 0


def test_save(db):
    db.save(alice)
    assert Employee(**db.get(alice.id)).id == alice.id


def test_delete(db):
    db.save(alice)
    assert Employee(**db.get(alice.id)).id == alice.id
    db.delete(alice.id)
    assert db.get(alice.id) is None


def test_get_all(db):
    db.save(alice)
    db.save(bob)
    assert db.get_all()[1].get('id') == bob.id
