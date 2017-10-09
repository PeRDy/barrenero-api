from rest_framework import permissions


class IsAPISuperuser(permissions.BasePermission):
    """
    Global permission check for blacklisted IPs.
    """

    def has_permission(self, request, view):
        return request.user.is_api_superuser
