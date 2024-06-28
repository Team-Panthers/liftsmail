# from django.shortcuts import render

from rest_framework import views, status
from rest_framework.response import Response
from django.contrib.auth import login, logout
from .serializers import LoginSerializer
from .services import authenticate_user

# Sample request data:
# {"email": "a@g.com", "password": "a"}


class LoginView(views.APIView):
    """
    Handles user login requests.
    """

    def post(self, request):
        """
        POST method to handle login.

        Validates the user credentials and logs in the user if they are correct.
        """
        # Deserialize and validate the request data
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            try:
                # Authenticate the user
                user, err = authenticate_user(email=email, password=password)
                # If there's an error during authentication, return a 400 response
                if err:
                    return Response(
                        {"message": err}, status=status.HTTP_400_BAD_REQUEST
                    )
                # Log in the user
                login(request, user)
                # Return a success message if login is successful
                return Response(
                    {"message": "Successfully logged in."}, status=status.HTTP_200_OK
                )
            except:
                # Catch any unexpected errors and return a 400 response
                return Response(
                    {"error": "Cannot authenticate user"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # Return a 400 response if the request data is invalid
        return Response(
            {"error": "An error occurred with the data provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LogoutView(views.APIView):
    """
    Handles user logout requests.
    """

    def post(self, request):
        """
        POST method to handle logout.

        Logs out the user and ends the session.
        """
        # Log out the user
        logout(request)
        # Return a success message if logout is successful
        return Response(
            {"message": "Successfully logged out."}, status=status.HTTP_200_OK
        )
