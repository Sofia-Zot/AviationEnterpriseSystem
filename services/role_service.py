from typing import List


class RoleService:
    # Иерархия ролей (от низкой к высокой)
    ROLE_HIERARCHY = {
        'analyst': 1,
        'tester': 2,
        'technologist': 3,
        'foreman': 4,
        'master': 5,
        'hr_manager': 6,
        'admin': 7,
    }

    # Какие запросы доступны каждой роли
    QUERY_ACCESS = {
        # analyst - только аналитика
        'analyst': [1, 2, 14],
        # tester - испытания и оборудование
        'tester': [1, 2, 8, 10, 11, 12, 13, 14],
        # technologist - техпроцессы и работы
        'technologist': [1, 2, 5, 8, 9, 14],
        # foreman - бригады и работы
        'foreman': [5, 6, 8, 9, 14],
        # master - всё кроме кадров
        'master': [1, 2, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14],
        # hr_manager - всё кроме кадров
        'hr_manager': [1, 2, 3, 4, 6, 7, 8, 14],
        # admin - всё
        'admin': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
    }

    @classmethod
    def has_permission(cls, user_role: str, required_role: str) -> bool:
        """
        Проверяет, достаточно ли прав у пользователя.

        Args:
            user_role: Роль пользователя.
            required_role: Требуемая роль.

        Returns:
            bool: True если у пользователя достаточно прав.
        """
        user_level = cls.ROLE_HIERARCHY.get(user_role.lower(), 0)
        required_level = cls.ROLE_HIERARCHY.get(required_role.lower(), 0)
        return user_level >= required_level

    @classmethod
    def get_accessible_queries(cls, user_role: str) -> List[int]:
        """
        Возвращает список номеров запросов, доступных роли.

        Args:
            user_role: Роль пользователя.

        Returns:
            List[int]: Список номеров доступных запросов (1-14).
        """
        return cls.QUERY_ACCESS.get(user_role.lower(), [])

    @classmethod
    def can_access_query(cls, user_role: str, query_number: int) -> bool:
        """
        Проверяет, может ли пользователь с данной ролью выполнить запрос.

        Args:
            user_role: Роль пользователя.
            query_number: Номер запроса (1-14).

        Returns:
            bool: True если доступ разрешён.
        """
        return query_number in cls.get_accessible_queries(user_role)

    @classmethod
    def get_role_level(cls, role: str) -> int:
        """
        Возвращает уровень роли в иерархии.

        Args:
            role: Название роли.

        Returns:
            int: Уровень роли (0 если неизвестная).
        """
        return cls.ROLE_HIERARCHY.get(role.lower(), 0)

    @classmethod
    def get_all_roles(cls) -> List[str]:
        """
        Возвращает список всех известных ролей.

        Returns:
            List[str]: Список ролей.
        """
        return list(cls.ROLE_HIERARCHY.keys())
