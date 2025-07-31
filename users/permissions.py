from rest_framework.permissions import BasePermission


class CanAssignWorkcell(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('catalog.add_workcelluser')

class CanUnassignWorkcell(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('catalog.delete_workcelluser')