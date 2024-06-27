from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import CustomUser

class CustomUserManagerTests(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email='test@example.com', password='password123')

        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(email='admin@example.com', password='adminpassword')

        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)

    def test_create_user_missing_email(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='password123')

    def test_create_superuser_not_staff(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='superuser@example.com', password='superpassword', is_staff=False)

    def test_create_superuser_not_superuser(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='superuser@example.com', password='superpassword', is_superuser=False)

class CustomUserModelTests(TestCase):

    def test_user_str_method(self):
        user = CustomUser(email='test@example.com')
        self.assertEqual(str(user), 'test@example.com')

    def test_user_is_verified_default_false(self):
        user = CustomUser(email='test@example.com')
        self.assertFalse(user.is_verified)
