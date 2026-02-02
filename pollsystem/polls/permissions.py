from rest_framework import permissions 

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a poll to edit it.
    Read-only access is allowed for everyone.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions (PUT, PATCH, DELETE) are only allowed for poll owner.
        # obj here is a Poll instance
        return obj.created_by == request.user