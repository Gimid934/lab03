"""Иерархия предметных исключений каталога."""


class CatalogError(Exception):
    """Базовое исключение каталога маршрутов."""

    def __init__(self, msg="") -> None:
        """Инициализировать сообщение ошибки."""
        self.msg = msg
        super().__init__(self.msg)


class InvalidRouteError(CatalogError):
    """Нарушение ограничений полей маршрута."""


class DuplicateIdError(CatalogError):
    """Добавление маршрута с существующим ID."""


class RouteNotFoundError(CatalogError):
    """Обращение к отсутствующему ID маршрута."""


class UnsupportedFormatVersionError(CatalogError):
    """Неподдерживаемая версия формата JSON."""


class CorruptedFileError(CatalogError):
    """Ошибка синтаксиса или структуры документа каталога."""
