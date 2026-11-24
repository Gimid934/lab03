"""Проверки обязательной части лабораторной работы 3."""
from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from src.errors import CatalogError, InvalidRouteError
from src.models import Route


def test_valid_route():
    """Создать dataclass со всеми полями маршрута."""
    route = Route("10", "Central park", "Bus", 2000, "Station", "Park", 12.5)
    assert is_dataclass(route)
    assert route.route_id == "10"
    assert route.name == "Central park"
    assert route.category == "Bus"
    assert route.launch_year == 2000
    assert route.start == "Station"
    assert route.end == "Park"
    assert route.distance_km == 12.5


def test_invalid_strings():
    """Отклонить пустые строки и неверные типы строковых полей."""
    for field in ("route_id", "name", "category", "start", "end"):
        for value in ("", "   ", None, 123):
            data = {
                "route_id": "10", "name": "Central park", "category": "Bus",
                "launch_year": 2000, "start": "Station", "end": "Park",
                "distance_km": 12.5,
            }
            data[field] = value
            with pytest.raises(InvalidRouteError) as exc_info:
                Route(**data)
            assert isinstance(exc_info.value, CatalogError)


def test_invalid_year():
    """Отклонить неположительный год и неверный тип."""
    for year in (0, -1, 2000.5, "2000", None, True):
        with pytest.raises(InvalidRouteError) as exc_info:
            Route("10", "Central park", "Bus", year, "Station", "Park", 12.5)
        assert isinstance(exc_info.value, CatalogError)


def test_invalid_distance():
    """Отклонить неверный тип, неположительное и бесконечное расстояние."""
    for distance in (0.0, -1.0, "12.5", None, True, float("nan"), float("inf")):
        with pytest.raises(InvalidRouteError) as exc_info:
            Route("10", "Central park", "Bus", 2000, "Station", "Park", distance)
        assert isinstance(exc_info.value, CatalogError)


def test_route_is_frozen():
    """Запретить изменение ID после создания."""
    route = Route("10", "Central park", "Bus", 2000, "Station", "Park", 12.5)
    with pytest.raises(FrozenInstanceError):
        route.route_id = "20"
