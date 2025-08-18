from typing import TypeVar
from django.contrib.auth.models import User
from django.db.models import QuerySet

from users.models import RoleScope
from users.services.access import resolve_scope

T = TypeVar('T')


class BaseService:
    def add_filter_by_rol(self, user: User, queryset: QuerySet[T]) -> QuerySet[T]:
        """
        [Tu documentación actual aquí]
        """
        scope = resolve_scope(user)

        if scope == RoleScope.ALL:
            return queryset
        elif scope == RoleScope.WORKCELL:
            return queryset.filter(project__work_cell__users=user)
        elif scope == RoleScope.OWNED:
            return queryset.filter(agent=user)
        else:
            return queryset.none()