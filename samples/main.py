"""Запуск из корня проекта: python -m samples.main."""

from pathlib import Path

from src.catalog import RouteCatalog
from src.models import Route
from src.storage import load_catalog, save_catalog


def main() -> None:
    """Показать основные операции с каталогом маршрутов."""
    catalog = RouteCatalog()
    catalog.add(Route("10", "Центральный", "Автобус", 2000, "Вокзал", "Парк", 12.5))
    catalog.add(Route("20", "Северный", "Трамвай", 2010, "Площадь", "Школа", 8.5))

    print("Всего маршрутов:", len(catalog))
    for route in catalog:
        print(route)

    print("Повторная итерация:")

    for route in catalog:
        print(route)

    print("По ID:", catalog.get("10"))
    print("По имени:", catalog.find_by_name("центральный"))
    print("По категории:", catalog.find_by_category("Автобус"))

    catalog.remove("20")
    print("После удаления ID 20 присутствует:", "20" in catalog)

    path = Path(__file__).resolve().parent / "routes.json"
    save_catalog(catalog, path)
    restored = RouteCatalog()
    load_catalog(restored, path)
    print("Загружено из JSON:", list(restored))


if __name__ == "__main__":
    main()
