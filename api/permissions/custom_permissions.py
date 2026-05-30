from rest_framework.permissions import (

    SAFE_METHODS,
    BasePermission,

)


class IsAdminUserRole(
    BasePermission
):

    message = (
        "Only admin users can access this endpoint."
    )

    def has_permission(
        self,
        request,
        view
    ):

        return (

            request.user.is_authenticated

            and request.user.role == 'admin'

        )


class IsAuthorUserRole(
    BasePermission
):

    message = (
        "Only author users can access this endpoint."
    )

    def has_permission(
        self,
        request,
        view
    ):

        return (

            request.user.is_authenticated

            and request.user.role == 'author'

        )


class IsAdminOrAuthorRole(
    BasePermission
):

    message = (
        "Only admin or author users can access this endpoint."
    )

    def has_permission(
        self,
        request,
        view
    ):

        return (

            request.user.is_authenticated

            and request.user.role in [

                'admin',
                'author'

            ]

        )


class IsAuthorOrReadOnly(
    BasePermission
):

    message = (
        "Only the author can modify this object."
    )

    def has_object_permission(

        self,
        request,
        view,
        obj

    ):

        if request.method in SAFE_METHODS:

            return True

        return obj.author == request.user