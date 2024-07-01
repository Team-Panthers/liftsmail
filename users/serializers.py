from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["email", "password"]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model,
    allowing to create,
    retrieve,
    update and
    delete a user's profile.
    """
    
    class Meta:
        """
        Meta class for the ProfileSerializer.

        Args:
            model (class): The model to be serialized.
            fields (list): The fields to be serialized.
        """
        model = CustomUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Initialize the ProfileSerializer.

        Args:
            args (tuple): The positional arguments.
            kwargs (dict): The keyword arguments.
        """
        super(ProfileSerializer, self).__init__(*args, **kwargs)
        if self.context['request'].method in ['PUT', 'PATCH']:
            """
            If the request method is 'PUT' or 'PATCH',
            the email and password fields are not required.
            """
            self.fields['email'].required = False
            self.fields['password'].required = False
