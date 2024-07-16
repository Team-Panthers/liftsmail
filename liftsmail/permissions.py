from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute or is related to a `Group`.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the object has an attribute `user`
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # If the object doesn't have `user`, assume it's related to a `Group`
        # Check if the requesting user is an owner of the group
        return obj.group.user == request.user