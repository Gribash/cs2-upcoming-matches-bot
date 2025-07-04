import os
import sqlite3
import tempfile
import pytest
from bot import db

@pytest.fixture
def temp_db_path():
    # Создание временного файла БД
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        yield tmp.name
    os.unlink(tmp.name)

def test_add_and_remove_subscriber(temp_db_path):
    db.DB_PATH = temp_db_path  # переназначаем путь к БД
    db.init_db()

    test_chat_id = 999999999
    db.add_subscriber(test_chat_id)

    subscribers = db.get_all_subscribers()
    assert test_chat_id in subscribers

    db.remove_subscriber(test_chat_id)
    subscribers = db.get_all_subscribers()
    assert test_chat_id not in subscribers