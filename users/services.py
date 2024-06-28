from django.contrib.auth import authenticate


def authenticate_user(email, password):
    if email and password:
        user = authenticate(email=email, password=password)
        if not user:
            return "error"
        return user
    else:
        return "error"
