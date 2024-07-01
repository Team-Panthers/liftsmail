from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

class RegisterTests(APITestCase):
    def test_register_user(self):
        """
        Ensure we can create a new user.
        """
        url = reverse('signup')
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email='test@example.com')
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('password123'))
    
    def test_register_user_with_existing_email(self):
        """
        Ensure that registering a user with an existing email fails.
        """
        get_user_model().objects.create_user(email='test@example.com', password='password123')
        url = reverse('signup')
        data = {
            'email': 'test@example.com',
            'password': 'newpassword456'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
