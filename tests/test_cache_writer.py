import os
import json
import time
from datetime import datetime
from utils.cache_writer import (
    write_json_to_cache,
    read_json_from_cache,
    get_cache_last_modified,
)

def test_write_and_read_cache(tmp_path, monkeypatch):
    # Переопределим путь к кэшу на временную папку
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    monkeypatch.setattr("utils.cache_writer.CACHE_DIR", str(cache_dir))

    name = "test"
    data = {"matches": [{"id": 1, "name": "Match A"}]}
    
    write_json_to_cache(name, data)
    result = read_json_from_cache(name)
    
    assert isinstance(result, dict)
    assert "matches" in result
    assert result["matches"][0]["id"] == 1

def test_get_cache_last_modified(tmp_path, monkeypatch):
    # Переопределим путь к кэшу на временную папку
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    monkeypatch.setattr("utils.cache_writer.CACHE_DIR", str(cache_dir))

    name = "test_modified"
    data = {"tournaments": [{"id": 100, "name": "Test Tournament"}]}

    write_json_to_cache(name, data)

    mtime = get_cache_last_modified(name)
    assert isinstance(mtime, datetime)

    file_path = cache_dir / f"{name}.json"
    assert file_path.exists()
    assert mtime.timestamp() <= time.time()

def test_read_nonexistent_cache(monkeypatch):
    monkeypatch.setattr("utils.cache_writer.CACHE_DIR", "/nonexistent/path")
    result = read_json_from_cache("no_such_file")
    assert result == {"matches": [], "updated_at": None}

def test_overwrite_existing_cache(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    monkeypatch.setattr("utils.cache_writer.CACHE_DIR", str(cache_dir))

    name = "test_overwrite"
    write_json_to_cache(name, {"matches": [{"id": 1}]})
    write_json_to_cache(name, {"matches": [{"id": 2}]})

    result = read_json_from_cache(name)
    assert result["matches"][0]["id"] == 2