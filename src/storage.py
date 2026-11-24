"""Сохранение и атомарная загрузка каталога в формате JSON."""

from dataclasses import asdict
from json import JSONDecodeError, dump, load
from pathlib import Path

from src.catalog import RouteCatalog
from src.constants import VERSION
from src.errors import CatalogError, CorruptedFileError, UnsupportedFormatVersionError
from src.models import Route


def save_catalog(catalog: RouteCatalog, path: str | Path) -> None:
    """Сохранить версию формата и все поля маршрутов в порядке добавления."""
    items = [asdict(route) for route in catalog]
    with open(path, "w", encoding="utf-8") as f:
        dump({"format_version": VERSION, "items": items}, f,
             indent=4, ensure_ascii=False, allow_nan=False)


def load_catalog(catalog: RouteCatalog, path: str | Path) -> None:
    """Заменить каталог данными JSON после полной проверки документа.

    При повреждении документа вызвать CorruptedFileError, при неизвестной
    версии — UnsupportedFormatVersionError. До завершения проверки состояние
    каталога не изменяется. Порядок записей файла сохраняется.
    """
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = load(f)
        except (JSONDecodeError, UnicodeDecodeError) as e:
            raise CorruptedFileError(f"Файл {path} повреждён") from e

    if not isinstance(data, dict):
        raise CorruptedFileError(f"Корень документа {path} должен быть объектом")
    if "format_version" not in data or type(data["format_version"]) is not int:
        raise CorruptedFileError(f"В файле {path} отсутствует целочисленная версия")
    if data["format_version"] != VERSION:
        raise UnsupportedFormatVersionError(
            f"Версия {data['format_version']} отклонена. Текущая версия {VERSION}"
        )
    if "items" not in data or not isinstance(data["items"], list):
        raise CorruptedFileError(f"В файле {path} не найден список маршрутов")

    temporary = RouteCatalog()
    for route in data["items"]:
        if not isinstance(route, dict):
            raise CorruptedFileError(f"Запись маршрута в файле {path} должна быть объектом")
        try:
            temporary.add(Route.from_dict(route))
        except (CatalogError, TypeError) as e:
            raise CorruptedFileError(f"Некорректная запись в файле {path}") from e

    catalog._items = temporary._items
