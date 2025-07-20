import os
import tempfile
import sqlite3
import pytest

# Импортируем функции из модуля db
from bot import db

@pytest.fixture
def temp_db_path(monkeypatch):
    # Создаём временный файл базы данных и переопределяем путь
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    monkeypatch.setattr(db, "DB_PATH", temp_file.name)
    db.init_db()
    yield temp_file.name
    os.remove(temp_file.name)

def test_add_subscriber(temp_db_path):
    user_id = 1001
    db.add_subscriber(user_id, tier="sa")
    assert user_id in db.get_all_subscribers()

def test_update_is_active(temp_db_path):
    user_id = 1002
    db.add_subscriber(user_id)
    db.update_is_active(user_id, False)
    assert not db.is_subscriber_active(user_id)
    db.update_is_active(user_id, True)
    assert db.is_subscriber_active(user_id)

def test_get_subscriber_tier(temp_db_path):
    user_id = 1003
    db.add_subscriber(user_id, tier="all")
    assert db.get_subscriber_tier(user_id) == "all"

def test_mark_and_get_notified(temp_db_path):
    user_id = 1004
    match_id = 9001
    db.add_subscriber(user_id)
    db.mark_notified(user_id, match_id)
    assert db.was_notified(user_id, match_id)

def test_mark_notified_bulk(temp_db_path):
    user_id = 1005
    db.add_subscriber(user_id)
    pairs = [(user_id, 111), (user_id, 222)]
    db.mark_notified_bulk(pairs)
    result = db.get_notified_match_ids(user_id)
    assert 111 in result and 222 in result

def test_update_tier(temp_db_path):
    user_id = 1006
    db.add_subscriber(user_id, tier="sa")
    db.update_tier(user_id, "all")
    assert db.get_subscriber_tier(user_id) == "all"

def test_get_all_subscribers(temp_db_path):
    user_id_1 = 1007
    user_id_2 = 1008
    db.add_subscriber(user_id_1)
    db.add_subscriber(user_id_2)
    subs = db.get_all_subscribers()
    assert user_id_1 in subs and user_id_2 in subs

def test_remove_subscriber(temp_db_path):
    user_id = 1009
    db.add_subscriber(user_id)
    db.remove_subscriber(user_id)
    assert not db.is_subscriber_active(user_id)