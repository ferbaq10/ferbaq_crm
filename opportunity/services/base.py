from typing import TypeVar
from django.contrib.auth.models import User
from django.db.models import QuerySet

from users.models import RoleScope
from users.services.access import resolve_scope

T = TypeVar('T')


class BaseService:
    def add_filter_by_rol(self,
                          user: User,
                          queryset: QuerySet[T],
                          workcell_filter_field: str = "project__work_cell__users") -> QuerySet[T]:
        """
        Args:
            workcell_filter_field: Campo para filtrar por work_cell (ej: "project__work_cell__users")
        """
        scope = resolve_scope(user)

        if scope == RoleScope.ALL:
            return queryset
        elif scope == RoleScope.WORKCELL:
            filter_kwargs = {workcell_filter_field: user}
            return queryset.filter(**filter_kwargs)
        elif scope == RoleScope.OWNED:
            return queryset.filter(agent=user)
        else:
            return queryset.none()