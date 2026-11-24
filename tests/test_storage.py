"""Проверки обязательной части лабораторной работы 3."""
import json
from dataclasses import asdict

import pytest

from src.catalog import RouteCatalog
from src.errors import CatalogError, CorruptedFileError, UnsupportedFormatVersionError
from src.models import Route
from src.storage import load_catalog, save_catalog


def test_json_round_trip(tmp_path):
    """Сохранить все поля, версию и порядок; загрузить вместо старых данных."""
    catalog = RouteCatalog()
    first = Route("20", "Северный парк", "Автобус", 2000, "Station", "Park", 12.5)
    second = Route("10", "Central park", "Tram", 2010, "Station", "Park", 8.5)
    catalog.add(first)
    catalog.add(second)
    path = tmp_path / "routes.json"
    save_catalog(catalog, path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["format_version"] == 1
    assert data["items"] == [asdict(first), asdict(second)]
    restored = RouteCatalog()
    restored.add(Route("old", "Central park", "Bus", 1990, "Station", "Park", 3.5))
    load_catalog(restored, path)
    assert [asdict(route) for route in restored] == [asdict(first), asdict(second)]
    assert "old" not in restored
    assert restored.get("20") == first
    assert list(restored.find_by_category("Tram")) == [second]


def test_empty_round_trip(tmp_path):
    """Сохранить и загрузить пустой каталог."""
    path = tmp_path / "empty.json"
    save_catalog(RouteCatalog(), path)
    catalog = RouteCatalog()
    catalog.add(Route("old", "Central park", "Bus", 1990, "Station", "Park", 3.5))
    load_catalog(catalog, path)
    assert len(catalog) == 0
    assert list(catalog) == []
    assert "old" not in catalog
    assert list(catalog.find_by_category("Bus")) == []


def test_corrupted_documents(tmp_path):
    """Отклонить повреждённый документ без изменения каталога."""
    path = tmp_path / "broken.json"
    catalog = RouteCatalog()
    old = Route("old", "Central park", "Bus", 1990, "Station", "Park", 3.5)
    catalog.add(old)
    for text in ('{', '[]', 'null', '42', '"text"', '{}', '{"items": []}',
                 '{"format_version": true, "items": []}',
                 '{"format_version": 1.0, "items": []}',
                 '{"format_version": "1", "items": []}',
                 '{"format_version": 1}', '{"format_version": 1, "items": {}}'):
        path.write_text(text, encoding="utf-8")
        with pytest.raises(CorruptedFileError) as exc_info:
            load_catalog(catalog, path)
        assert isinstance(exc_info.value, CatalogError)
        assert list(catalog) == [old]
        assert catalog.get("old") == old


def test_unknown_version(tmp_path):
    """Отклонить неизвестную версию без изменения каталога."""
    path = tmp_path / "future.json"
    path.write_text(json.dumps({"format_version": 999, "items": []}), encoding="utf-8")
    catalog = RouteCatalog()
    old = Route("old", "Central park", "Bus", 1990, "Station", "Park", 3.5)
    catalog.add(old)
    with pytest.raises(UnsupportedFormatVersionError) as exc_info:
        load_catalog(catalog, path)
    assert isinstance(exc_info.value, CatalogError)
    assert list(catalog) == [old]


def test_error_in_middle_is_atomic(tmp_path):
    """Ошибка второй записи оставляет каталог и индексы неизменными."""
    catalog = RouteCatalog()
    old = Route("old", "Central park", "Bus", 1990, "Station", "Park", 3.5)
    catalog.add(old)
    first = asdict(Route("new", "Central park", "Tram", 2010, "Station", "Park", 8.5))
    last = asdict(Route("last", "Central park", "Tram", 2020, "Station", "Park", 6.5))
    invalid = dict(first)
    invalid["route_id"] = "bad"
    invalid["name"] = "   "
    missing = dict(first)
    del missing["start"]
    path = tmp_path / "partial.json"
    for bad_item in (invalid, missing, dict(first), 42):
        data = {"format_version": 1, "items": [first, bad_item, last]}
        path.write_text(json.dumps(data), encoding="utf-8")
        with pytest.raises(CorruptedFileError) as exc_info:
            load_catalog(catalog, path)
        assert isinstance(exc_info.value, CatalogError)
        assert list(catalog) == [old]
        assert len(catalog) == 1
        assert catalog.get("old") == old
        assert "new" not in catalog
        assert "last" not in catalog
        assert list(catalog.find_by_category("Bus")) == [old]
        assert list(catalog.find_by_category("Tram")) == []
