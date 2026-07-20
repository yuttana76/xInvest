from rest_framework import permissions

class IsOperator(permissions.BasePermission):
    """
    Allows access only to users in the 'operator' group.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='operator').exists())

class IsMarketing(permissions.BasePermission):
    """
    Allows access only to users in the 'marketing' group.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='marketing').exists())

class IsAgent(permissions.BasePermission):
    """
    Allows access only to users in the 'agent' group.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='agent').exists())
