"""Модель маршрута и проверка ограничений её полей."""

from dataclasses import dataclass
from math import isfinite

from src.errors import InvalidRouteError


@dataclass(frozen=True)
class Route:
    """Неизменяемый маршрут с ID, названием, категорией и параметрами пути."""

    route_id: str
    name: str
    category: str
    launch_year: int
    start: str
    end: str
    distance_km: float

    def __post_init__(self) -> None:
        """Проверить непустые строки, положительный год и конечное расстояние.

        Год имеет тип int, расстояние — float и строго больше нуля.
        При нарушении ограничений вызвать InvalidRouteError.
        """
        self.check_str(self.route_id, "ID должен быть непустой строкой")
        self.check_str(self.name, "Имя должно быть непустой строкой")
        self.check_str(self.category, "Категория должна быть непустой строкой")
        self.check_str(self.start, "Начало должно быть непустой строкой")
        self.check_str(self.end, "Конец должен быть непустой строкой")
        if type(self.launch_year) is not int or self.launch_year <= 0:
            raise InvalidRouteError("Год открытия должен быть целым положительным числом")
        if type(self.distance_km) is not float or\
           not isfinite(self.distance_km) or\
           self.distance_km <= 0:
            raise InvalidRouteError("Протяжённость должна быть положительным числом")

    def check_str(self, var: str, errmsg: str) -> None:
        """Вызвать InvalidRouteError, если значение не строка или пусто после strip."""
        if not isinstance(var, str) or not var.strip():
            raise InvalidRouteError(errmsg)

    @classmethod
    def from_dict(cls, data: dict) -> "Route":
        """Создать маршрут из словаря полей."""
        return cls(**data)
