from rest_framework import permissions


class IsAccountOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user:
            return obj == request.user
        return False


class IsAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user:
            return request.user.is_admin
        return False


class IsStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user:
            return request.user.is_staff
        return False