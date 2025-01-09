from rest_framework.permissions import BasePermission

from rest_framework.exceptions import PermissionDenied

class IsActiveUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_active


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):   
        return request.user.is_authenticated and request.user.is_superuser


class IsGroupAdmin(BasePermission):
   
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user == obj.admin:
            return True
        return False
    
class IsGroupMember(BasePermission):
   
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and  request.user in obj.members.all():
            return True
        return False