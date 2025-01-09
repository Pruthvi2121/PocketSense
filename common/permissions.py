from rest_framework.permissions import BasePermission

from rest_framework.exceptions import PermissionDenied

class IsActiveUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_active


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):   
        return request.user.is_authenticated and request.user.is_superuser

