from rest_framework import permissions
from .models import Employer, User

UNAVAILABLE_LIST = [User.STATUS.suspended, User.STATUS.deleted, User.STATUS.black_listed]
INACTIVE_LIST = [User.STATUS.inactive, User.STATUS.suspended, User.STATUS.deleted, User.STATUS.black_listed]


class IsAccountOwner(permissions.BasePermission):
    """
    user can only update his own account
    """
    def has_object_permission(self, request, view, obj):
        if request.user:
            if hasattr(obj, 'user'):
                return obj.user == request.user
            return obj == request.user
        return False


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and not request.user.is_anonymous():
            return request.user.is_admin
        return False


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and not request.user.is_anonymous():
            return request.user.is_superAdmin
        return False


class IsActiveUser(permissions.BasePermission):
    """
    only active user can access the job functions
    """
    def has_permission(self, request, view):
        if request.user and not request.user.is_anonymous():
            check = int(request.user.status) not in INACTIVE_LIST
            return check
        return False


class IsAvailableUser(permissions.BasePermission):
    """
    only available user can access the base functions
    """
    def has_permission(self, request, view):
        if request.user and not request.user.is_anonymous():
            check = int(request.user.status) not in UNAVAILABLE_LIST
            return check
        return False


class IsEmployer(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and not request.user.is_anonymous():
            return request.user.app_user_type == 'Employer'
        return False


class IsJOIE(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and not request.user.is_anonymous():
            return request.user.app_user_type == 'JOIE'
        return False


class IsApplicationOwner(permissions.BasePermission):
    """
    user can only access his own applications info
    """
    def has_permission(self, request, view):
        permission = True
        if request.user:
            emp = Employer.objects.get(user=request.user)
            for application in view.get_queryset():
                if application.job.owner != emp:
                    permission = False
        return permission