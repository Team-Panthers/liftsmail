from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


def authenticate_user(email, password):
    user = authenticate(email=email, password=password)
    if user is None:
        return None, "Invalid email or password."
    
    token, created = Token.objects.get_or_create(user=user)
    return user, token.key
