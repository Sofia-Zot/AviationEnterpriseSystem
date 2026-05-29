from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional


T = TypeVar('T')


class BaseDAO(ABC, Generic[T]):
    @abstractmethod
    def get_all(self) -> List[T]:
        """Возвращает список всех записей."""
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Возвращает запись по идентификатору."""
        pass

    @abstractmethod
    def insert(self, entity: T) -> bool:
        """Добавляет новую запись. При успехе обновляет id сущности."""
        pass

    @abstractmethod
    def update(self, entity: T) -> bool:
        """Обновляет существующую запись."""
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Удаляет запись по идентификатору."""
        pass
