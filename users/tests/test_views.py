from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

class UserRegisterTests(APITestCase):
    
    @patch('allauth.account.models.EmailAddress.send_confirmation')
    def test_register_user(self, mock_send_confirmation):
        """
        Ensure we can create a new user.
        """
        url = reverse('rest_register')
        data = {
            'email': 'test@example.com',
            'password1': 'complexpassword',
            'password2': 'complexpassword'
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        user = get_user_model().objects.get(email='test@example.com')
        self.assertIsNotNone(user)
        assert mock_send_confirmation.called
        self.assertTrue(user.check_password('complexpassword'))

    def test_register_user_with_existing_email(self):
        """
        Ensure that registering a user with an existing email fails.
        """
        get_user_model().objects.create_user(email='test@example.com', password='password123')
        url = reverse('rest_register')
        data = {
            'email': 'test@example.com',
            'password1': 'complexpassword',
            'password2': 'complexpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)