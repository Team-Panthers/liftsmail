
from rest_framework import generics
from .serializers import RegisterSerializer
# Create your views here.


class Register(generics.CreateAPIView):
    serializer_class = RegisterSerializer