from rest_framework import permissions

from user.models import Profile


class IsOwnerOrIsAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_staff


class IsUserHaveProfile(permissions.BasePermission):
    def has_permission(self, request, view):
        return Profile.objects.filter(user=request.user).exists()
