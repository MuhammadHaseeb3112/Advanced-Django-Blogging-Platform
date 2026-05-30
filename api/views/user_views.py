from django.contrib.auth.password_validation import (
    validate_password,
    
)

from django.core.exceptions import ValidationError
from rest_framework import status

from rest_framework.generics import (

    RetrieveAPIView,
    RetrieveUpdateAPIView,

)

from rest_framework.permissions import (
    IsAuthenticated
)

from rest_framework.response import (
    Response
)

from rest_framework.views import (
    APIView
)

from api.permissions.custom_permissions import (

    IsAdminUserRole,
    IsAuthorUserRole,

)

from api.serializers.user_serializers import (
    UserSerializer
)


# =========================================
# USER PROFILE API
# =========================================

class UserAPIView(
    RetrieveAPIView
):

    serializer_class = UserSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_object(self):

        return self.request.user


# =========================================
# PROFILE VIEW
# =========================================

class ProfileView(
    APIView
):

    permission_classes = [
        IsAuthenticated
    ]

    def get(
        self,
        request
    ):

        return Response({

            'success': True,

            'user': {

                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'role': request.user.role,
                'bio': request.user.bio,
                'profile_image': (
                    request.user.profile_image.url
                    if request.user.profile_image
                    else None
                ),

            }

        })


# =========================================
# PROFILE UPDATE API
# =========================================

class ProfileUpdateAPIView(
    RetrieveUpdateAPIView
):

    serializer_class = UserSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_object(self):

        return self.request.user


# =========================================
# CHANGE PASSWORD API
# =========================================

class ChangePasswordAPIView(
    APIView
):

    permission_classes = [
        IsAuthenticated
    ]

    def post(
        self,
        request
    ):

        user = request.user

        old_password = request.data.get(
            'old_password'
        )

        new_password = request.data.get(
            'new_password'
        )

        if not user.check_password(
            old_password
        ):

            return Response({

                'success': False,

                'message': (
                    'Old password incorrect'
                )

            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password)

        except ValidationError as e:
            return Response(
            {
            'success': False,
            'errors': e.messages
            },
            status=status.HTTP_400_BAD_REQUEST
        )

        user.set_password(
            new_password
        )

        user.save()

        return Response({

            'success': True,

            'message': (
                'Password changed successfully'
            )

        })


# =========================================
# ADMIN ONLY API
# =========================================

class AdminOnlyAPIView(
    APIView
):

    permission_classes = [
        IsAdminUserRole
    ]

    def get(
        self,
        request
    ):

        return Response({

            'success': True,
            'message': 'Welcome Admin'

        })


# =========================================
# AUTHOR ONLY API
# =========================================

class AuthorOnlyAPIView(
    APIView
):

    permission_classes = [
        IsAuthorUserRole
    ]

    def get(
        self,
        request
    ):

        return Response({

            'success': True,
            'message': 'Welcome Author'

        })