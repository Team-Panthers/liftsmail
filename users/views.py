# from django.shortcuts import render

from rest_framework import views, status
from rest_framework.response import Response
from django.contrib.auth import login, logout
from .serializers import LoginSerializer
from .services import authenticate_user

# Create your views here.


class LoginView(views.APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            try:
                user = authenticate_user(
                    email=email, password=password, request=request
                )
                login(request, user)
                return Response(
                    {"detail": "Successfully logged in."}, status=status.HTTP_200_OK
                )
            except ValueError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(views.APIView):
    def post(self, request):
        logout(request)
        return Response(
            {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
        )
