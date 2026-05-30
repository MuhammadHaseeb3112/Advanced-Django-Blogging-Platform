from rest_framework.permissions import BasePermission


class IsAuthorOrReadOnly(BasePermission):

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):

        # SAFE METHODS
        if request.method in ['GET', 'HEAD', 'OPTIONS']:

            return True

        # ADMIN ACCESS
        if request.user.role == 'admin':

            return True

        # AUTHOR ACCESS
        return obj.author == request.user