from rest_framework import serializers

from accounts.models import CustomUser

from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer
)


# =========================================
# USER SERIALIZER
# =========================================

class UserSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = CustomUser

        fields = [

            'id',
            'username',
            'email',
            'bio',
            'role',
            'profile_image',

        ]

        read_only_fields = [

            'id',
            'role',

        ]


# =========================================
# REGISTER SERIALIZER
# =========================================

class RegisterSerializer(
    serializers.ModelSerializer
):

    password = serializers.CharField(

        write_only=True,

        min_length=8

    )

    class Meta:

        model = CustomUser

        fields = [

            'username',
            'email',
            'password',

        ]

        extra_kwargs = {

            'password': {

                'write_only': True

            }

        }

    def validate_email(
        self,
        value
    ):

        if CustomUser.objects.filter(
            email=value
        ).exists():

            raise serializers.ValidationError(
                'Email already exists.'
            )

        return value

    def validate_username(
        self,
        value
    ):

        if CustomUser.objects.filter(
            username=value
        ).exists():

            raise serializers.ValidationError(
                'Username already exists.'
            )

        return value

    def create(
        self,
        validated_data
    ):

        user = CustomUser.objects.create_user(

            username=validated_data['username'],

            email=validated_data['email'],

            password=validated_data['password'],

        )

        return user


# =========================================
# JWT SERIALIZER
# =========================================

class CustomTokenObtainPairSerializer(
    TokenObtainPairSerializer
):

    @classmethod
    def get_token(
        cls,
        user
    ):

        token = super().get_token(
            user
        )

        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role

        return token

    def validate(
        self,
        attrs
    ):

        data = super().validate(
            attrs
        )

        if not self.user.email_verified:

            raise serializers.ValidationError(
                'Please verify your email first.'
            )

        data['user'] = {

            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,

        }

        return data