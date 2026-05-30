from rest_framework import status

from rest_framework.generics import (
    CreateAPIView
)

from rest_framework.permissions import (

    AllowAny,
    IsAuthenticated,

)

from rest_framework.response import (
    Response
)

from rest_framework.views import (
    APIView
)

from rest_framework_simplejwt.tokens import (
    RefreshToken
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView
)

from rest_framework_simplejwt.exceptions import (
    TokenError
)

from api.serializers.user_serializers import (

    RegisterSerializer,
    CustomTokenObtainPairSerializer,

)

from api.services.email_service import (
    send_verification_email
)


# =========================================
# CUSTOM JWT LOGIN VIEW
# =========================================

class CustomTokenObtainPairView(
    TokenObtainPairView
):

    serializer_class = (
        CustomTokenObtainPairSerializer
    )


# =========================================
# REGISTER API
# =========================================

class RegisterAPIView(
    CreateAPIView
):

    serializer_class = RegisterSerializer

    permission_classes = [
        AllowAny
    ]

    def create(
        self,
        request,
        *args,
        **kwargs
    ):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        send_verification_email(

            request,
            user

        )

        return Response(

            {
                'success': True,

                'message': (
                    'Registration successful. '
                    'Please verify your email.'
                ),

                'data': serializer.data,
            },

            status=status.HTTP_201_CREATED

        )


# =========================================
# LOGOUT API
# =========================================

class LogoutAPIView(
    APIView
):

    permission_classes = [
        IsAuthenticated
    ]

    def post(
        self,
        request
    ):

        try:

            refresh_token = request.data.get(
                "refresh"
            )

            if not refresh_token:

                return Response(

                    {
                        "success": False,
                        "message": (
                            "Refresh token is required."
                        )
                    },

                    status=status.HTTP_400_BAD_REQUEST

                )

            token = RefreshToken(
                refresh_token
            )

            token.blacklist()

            return Response(

                {
                    "success": True,
                    "message": "Logout successful"
                },

                status=status.HTTP_205_RESET_CONTENT

            )

        except TokenError:

            return Response(

                {
                    "success": False,
                    "message": "Invalid token"
                },

                status=status.HTTP_400_BAD_REQUEST

            )