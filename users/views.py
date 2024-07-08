from allauth.account.utils import send_email_confirmation
from django.contrib.auth import get_user_model
from rest_framework import generics,status
from rest_framework.response import Response
from .serializers import RegisterSerializer,PasswordResetSerializer


# Create your views here.


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer



class PasswordResetView(generics.CreateAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user_model = get_user_model()
            try:
                user = user_model.objects.get(email=email)
                # If the user is found, send the email confirmation
                send_email_confirmation(request, user)
                return Response({'message': 'Password reset link sent to your email'}, status=status.HTTP_200_OK)
            except user_model.DoesNotExist:
                # Handle the case where the user is not found
                return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)