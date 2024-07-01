from rest_framework import generics
from .serializers import RegisterSerializer, ProfileSerializer
from rest_framework import permissions, response
# Create your views here.


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class ProfileView(generics.RetrieveAPIView):
    """
    Profile View
    
    This class-based view provides the ability
    to retrieve the profile of the logged in user.
    It is accessible only to authenticated users.
    
    Attributes:
        permission_classes (list):
            A list of permission classes that this view requires.
        serializer_class (class):
            The serializer class that this view uses.
        
    Methods:
        get_object(self): Retrieve and return the current user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        """
        Get the current user.
        
        This method retrieves and returns the current user.
        
        Returns:
            User: The current user.
        """
        return self.request.user


class ProfileUpdateView(generics.UpdateAPIView):
    """
    Profile Update View
    
    This class-based view provides the ability
    to update the profile of the logged in user.
    It is accessible only to authenticated users.
    
    Attributes:
        permission_classes (list):
            A list of permission classes that this view requires.
        serializer_class (class):
            The serializer class that this view uses.
    
    Methods:
        get_object(self): Retrieve and return the current user.
        update(self, request, *args, **kwargs):
            Update the profile of the logged in user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        """
        Get the current user.
        
        This method retrieves and returns the current user.
        
        Returns:
            User: The current user.
        """
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        Update the profile of the logged in user.
        
        The method first retrieves the object representing the current user.
        It then creates a serializer instance with the retrieved object
        and the provided data.
        The serializer is validated, and if it is valid,
        the update is performed using the perform_update method.
        Finally, the updated data is returned in a response.
        
        Args:
            request (HttpRequest):
                The request object containing the data to update the profile.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        
        Returns:
            Response: The response containing the updated profile data.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return response.Response(serializer.data)
