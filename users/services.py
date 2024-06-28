from django.contrib.auth import authenticate


def authenticate_user(email, password):
    if email and password:
        user = authenticate(email=email, password=password)
        if not user:
            return None, "User cannot be found"
        return user, None
    else:
        return None, "Email and password is required"
