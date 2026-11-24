"""Проверки обязательной части лабораторной работы 3."""
import pytest

from src.catalog import RouteCatalog
from src.errors import CatalogError, DuplicateIdError, RouteNotFoundError
from src.models import Route


def test_empty_catalog():
    """Проверить операции над пустым каталогом."""
    catalog = RouteCatalog()
    assert len(catalog) == 0
    assert list(catalog) == []
    assert "10" not in catalog
    assert list(catalog.find_by_name("PARK")) == []
    assert list(catalog.find_by_category("Bus")) == []


def test_add_get_remove():
    """Добавить, получить и удалить маршрут по ID."""
    catalog = RouteCatalog()
    route = Route("10", "Central park", "Bus", 2000, "Station", "Park", 12.5)
    assert catalog.add(route) is None
    assert catalog.get("10") == route
    assert len(catalog) == 1
    assert "10" in catalog
    catalog.remove("10")
    assert len(catalog) == 0
    assert "10" not in catalog
    assert list(catalog) == []
    with pytest.raises(RouteNotFoundError) as exc_info:
        catalog.get("10")
    assert isinstance(exc_info.value, CatalogError)


def test_duplicate_id():
    """Запретить повторный ID, сохранив исходный маршрут."""
    catalog = RouteCatalog()
    first = Route("10", "Central park", "Bus", 2000, "Station", "Park", 12.5)
    second = Route("10", "Central park", "Tram", 2010, "Station", "Park", 8.5)
    catalog.add(first)
    with pytest.raises(DuplicateIdError) as exc_info:
        catalog.add(second)
    assert isinstance(exc_info.value, CatalogError)
    assert len(catalog) == 1
    assert catalog.get("10") == first
    assert list(catalog.find_by_category("Tram")) == []


def test_missing_id():
    """Вызвать предметную ошибку для отсутствующего ID."""
    catalog = RouteCatalog()
    route = Route("10", "Central park", "Bus", 2000, "Station", "Park", 12.5)
    catalog.add(route)
    with pytest.raises(RouteNotFoundError) as exc_info:
        catalog.get("missing")
    assert isinstance(exc_info.value, CatalogError)
    with pytest.raises(RouteNotFoundError) as exc_info:
        catalog.remove("missing")
    assert isinstance(exc_info.value, CatalogError)
    assert list(catalog) == [route]


def test_search_and_removal():
    """Проверить поиск и обновление результатов после удаления."""
    catalog = RouteCatalog()
    first = Route("20", "Central park", "Bus", 2000, "Station", "Park", 12.5)
    second = Route("10", "Central park", "Tram", 2010, "Station", "Park", 8.5)
    third = Route("30", "Central", "Bus", 2020, "Station", "Park", 6.5)
    for route in (first, second, third):
        catalog.add(route)
    assert list(catalog.find_by_category("Bus")) == [first, third]
    assert list(catalog.find_by_category("Metro")) == []
    assert list(catalog.find_by_name("CENTRAL PARK")) == [first, second]
    assert list(catalog.find_by_name("cEnTrAl PaRk")) == [first, second]
    assert list(catalog.find_by_name("park")) == []
    assert list(catalog.find_by_category("")) == [first, second, third]
    assert list(catalog.find_by_name("")) == [first, second, third]
    assert list(catalog.find_by_name("missing")) == []
    catalog.remove("20")
    assert list(catalog.find_by_category("Bus")) == [third]
    assert list(catalog.find_by_name("CENTRAL PARK")) == [second]
    assert "20" not in catalog


def test_iteration_order():
    """Сохранить порядок добавления при повторной итерации."""
    catalog = RouteCatalog()
    first = Route("20", "Central park", "Bus", 2000, "Station", "Park", 12.5)
    second = Route("10", "Central park", "Tram", 2010, "Station", "Park", 8.5)
    catalog.add(first)
    catalog.add(second)
    assert list(catalog) == [first, second]
    assert list(catalog) == [first, second]
    catalog.remove("20")
    catalog.add(first)
    assert list(catalog) == [second, first]


def test_search_results_do_not_change_catalog():
    """Изменение результата поиска не меняет каталог."""
    catalog = RouteCatalog()
    route = Route("10", "Central park", "Bus", 2000, "Station", "Park", 12.5)
    catalog.add(route)
    by_name = catalog.find_by_name("central park")
    by_category = catalog.find_by_category("Bus")
    assert isinstance(by_name, (list, tuple))
    assert isinstance(by_category, (list, tuple))
    if isinstance(by_name, list):
        by_name.clear()
    if isinstance(by_category, list):
        by_category.clear()
    assert len(catalog) == 1
    assert catalog.get("10") == route
    assert list(catalog) == [route]
    assert list(catalog.find_by_name("central park")) == [route]
    assert list(catalog.find_by_category("Bus")) == [route]
