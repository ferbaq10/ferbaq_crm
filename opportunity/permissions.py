from rest_framework.permissions import BasePermission
from users.models import RoleScope
from users.services.access import resolve_scope

class CanAccessOpportunity(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True

        scope = resolve_scope(user)
        if scope == RoleScope.ALL:
            return True
        if scope == RoleScope.OWNED:
            return obj.agent_id == user.id
        if scope == RoleScope.WORKCELL:
            # evita consultas N+1 si no tienes prefetched: usa IDs
            return obj.project and obj.project.work_cell and \
                   obj.project.work_cell.users.filter(id=user.id).exists()
        return False
