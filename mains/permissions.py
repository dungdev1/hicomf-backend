from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object level permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS request.
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return obj.user == request.user


class AllowPostOwnerDelete(permissions.BasePermission):
    """
    Object level permission to allow post owner can delete comment.
    """
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE' and obj.post.user == request.user:
            return True
        return False