from django.test import TestCase
from django.contrib.auth import get_user_model
from users.services import authenticate_user

# Get the custom user model
User = get_user_model()


class AuthenticateUserTests(TestCase):
    """
    Tests for the authenticate_user function in the services.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.email = "testuser@example.com"
        self.password = "testpassword"
        self.user = User.objects.create_user(email=self.email, password=self.password)

    def test_authenticate_user_success(self):
        """
        Test that authenticate_user returns the correct user for valid credentials.
        """
        # Call authenticate_user with valid credentials
        user, _ = authenticate_user(email=self.email, password=self.password)

        # Assert that the returned user matches the created user
        self.assertEqual(user, self.user)

    def test_authenticate_user_invalid_credentials(self):
        """
        Test that authenticate_user returns an error message for invalid credentials.
        """
        # Call authenticate_user with invalid password
        _, err = authenticate_user(email=self.email, password="wrongpassword")

        # Assert that the error message matches the expected message
        self.assertEqual(err, "User cannot be found")

    def test_authenticate_user_missing_email(self):
        """
        Test that authenticate_user returns an error message when email is missing.
        """
        # Call authenticate_user with missing email
        _, err = authenticate_user(email="", password=self.password)

        # Assert that the error message matches the expected message
        self.assertEqual(err, "Email and password is required")

    def test_authenticate_user_missing_password(self):
        """
        Test that authenticate_user returns an error message when password is missing.
        """
        # Call authenticate_user with missing password
        _, err = authenticate_user(email=self.email, password="")

        # Assert that the error message matches the expected message
        self.assertEqual(err, "Email and password is required")
