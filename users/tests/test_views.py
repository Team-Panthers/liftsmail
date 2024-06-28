from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model
from users.views import LoginView, LogoutView
from django.contrib.sessions.middleware import SessionMiddleware

# Get the custom user model
User = get_user_model()


class LoginViewTests(TestCase):
    """
    Tests for the LoginView.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.factory = RequestFactory()
        self.email = "testuser@example.com"
        self.password = "testpassword"
        self.user = User.objects.create_user(email=self.email, password=self.password)

    def test_login_view_success(self):
        """
        Test that the login view successfully logs in a user with valid credentials.
        """
        request = self.factory.post(
            "/login/", data={"email": self.email, "password": self.password}
        )

        # Add session to the request
        middleware = SessionMiddleware(lambda x: x)
        middleware.process_request(request)
        request.session.save()

        # Call the login view with the request
        response = LoginView.as_view()(request)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Check that the response contains the success message
        self.assertEqual(response.data["message"], "Successfully logged in.")

    def test_login_view_invalid_credentials(self):
        """
        Test that the login view returns an error for invalid credentials.
        """
        request = self.factory.post(
            "/login/", data={"email": self.email, "password": "wrongpassword"}
        )

        # Call the login view with the request
        response = LoginView.as_view()(request)

        # Check that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        # Check that the response contains the error message
        self.assertEqual(response.data["message"], "User cannot be found")

    def test_login_view_missing_email(self):
        """
        Test that the login view returns an error when email is missing.
        """
        request = self.factory.post(
            "/login/", data={"email": "", "password": self.password}
        )

        # Call the login view with the request
        response = LoginView.as_view()(request)

        # Check that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        # Check that the response contains the error message
        self.assertEqual(
            response.data["error"], "An error occurred with the data provided"
        )

    def test_login_view_missing_password(self):
        """
        Test that the login view returns an error when password is missing.
        """
        request = self.factory.post(
            "/login/", data={"email": self.email, "password": ""}
        )

        # Call the login view with the request
        response = LoginView.as_view()(request)

        # Check that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        # Check that the response contains the error message
        self.assertEqual(
            response.data["error"], "An error occurred with the data provided"
        )


class LogoutViewTests(TestCase):
    """
    Tests for the LogoutView.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.factory = RequestFactory()
        self.email = "testuser@example.com"
        self.password = "testpassword"
        self.user = User.objects.create_user(email=self.email, password=self.password)

    def test_logout_view_success(self):
        """
        Test that the logout view successfully logs out a logged-in user.
        """
        client = Client()
        request = self.factory.post("/logout/")

        # Force login the user
        client.force_login(user=self.user)

        # Add session to the request
        middleware = SessionMiddleware(lambda x: x)
        middleware.process_request(request)
        request.session.save()

        # Call the logout view with the request
        response = LogoutView.as_view()(request)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Check that the response contains the success message
        self.assertEqual(response.data["message"], "Successfully logged out.")
