from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer


User = get_user_model()

class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id','email','password','first_name','last_name')
    




















# from django.contrib.auth import get_user_model
# from rest_framework import serializers
# from dj_rest_auth.serializers import LoginSerializer as RestAuthSerilaizer
# from dj_rest_auth.registration.serializers import RegisterSerializer
# from allauth.account import app_settings as allauth_account_settings
# from allauth.account.adapter import get_adapter


# class LoginSerializer(RestAuthSerilaizer):
#     email = serializers.EmailField(required=False, allow_blank=True)
#     password = serializers.CharField(style={'input_type': 'password'})


# class CustomRegisterSerializer(RegisterSerializer):
#     def validate_email(self, email):
#         email = get_adapter().clean_email(email)
#         if allauth_account_settings.UNIQUE_EMAIL:
#             if get_user_model().objects.filter(email=email).exists():
#                 raise serializers.ValidationError(
#                     ('A user is already registered with this e-mail address.'),
#                 )
#         return email
