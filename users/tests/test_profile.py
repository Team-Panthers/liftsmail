from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileViewTests(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(email='test@example.com', password='testpassword123')
        self.client.login(email='test@example.com', password='testpassword123')

        # Obtain a token (assuming you have a token authentication mechanism)
        response = self.client.post(reverse('token_obtain_pair'), {'email': 'test@example.com', 'password': 'testpassword123'})
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_retrieve_profile(self):
        """
        Ensure we can retrieve the profile of the logged in user.
        """
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_update_profile(self):
        """
        Ensure we can update the profile of the logged in user.
        """
        new_first_name = 'UpdatedName'
        response = self.client.put(reverse('update-profile'), {'first_name': new_first_name}, format='json')
        if response.status_code != status.HTTP_200_OK:
            print(response.data)  # Debugging line to print out response data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, new_first_name)
