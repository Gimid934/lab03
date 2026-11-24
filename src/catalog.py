"""Каталог маршрутов со словарным индексом по ID."""

from collections.abc import Iterator

from src.errors import DuplicateIdError, RouteNotFoundError
from src.models import Route


class RouteCatalog:
    """Каталог с индексом по ID и итерацией в порядке добавления."""

    def __init__(self) -> None:
        """Создать пустой каталог."""
        self._items: dict[str, Route] = {}

    def add(self, el: Route) -> None:
        """Добавить маршрут; при повторном ID вызвать DuplicateIdError."""
        if el.route_id in self:
            raise DuplicateIdError(f"Маршрут {el.route_id} уже существует")
        self._items[el.route_id] = el

    def get(self, item_id: str) -> Route:
        """Получить маршрут по ID; при отсутствии вызвать RouteNotFoundError."""
        if item_id not in self:
            raise RouteNotFoundError(f"Маршрут {item_id} не найден")
        return self._items[item_id]

    def remove(self, item_id: str) -> None:
        """Удалить маршрут по ID; при отсутствии вызвать RouteNotFoundError."""
        if item_id not in self:
            raise RouteNotFoundError(f"Маршрут {item_id} не найден")
        self._items.pop(item_id)

    def find_by_category(self, category: str) -> tuple[Route, ...]:
        """Вернуть совпадения категории в порядке добавления.

        Категория сравнивается точно. Пустая категория возвращает все маршруты.
        Результат является отдельным кортежем.
        """
        if category == "":
            return tuple(self._items.values())
        return tuple(el for el in self._items.values() if el.category == category)

    def find_by_name(self, name: str) -> tuple[Route, ...]:
        """Вернуть полные совпадения имени без учёта регистра.

        Пустое имя возвращает все маршруты. Результат является отдельным
        кортежем в порядке добавления.
        """
        if name == "":
            return tuple(self._items.values())
        s = name.casefold()
        return tuple(el for el in self._items.values() if el.name.casefold() == s)

    def __len__(self) -> int:
        """Вернуть количество маршрутов."""
        return len(self._items)

    def __iter__(self) -> Iterator[Route]:
        """Вернуть итератор маршрутов в порядке добавления.

        Повторное добавление после удаления помещает маршрут в конец.
        """
        return iter(self._items.values())

    def __contains__(self, item_id: str) -> bool:
        """Проверить наличие ID в словарном индексе."""
        return item_id in self._items
