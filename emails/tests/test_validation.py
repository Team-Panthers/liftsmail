from rest_framework.test import APITestCase
from emails.models import Contact, Group
from emails.serializers import ContactSerializer, ProcessEmailsSerializer, ContactListSerializer
import tempfile
import json
import pandas as pd
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

User = get_user_model()



class ContactListSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='testuser', password='testpass')
        self.group = Group.objects.create(name="Test Group", user=self.user)

    def test_contact_list_serializer_valid_data(self):
        data = {
            'contacts': [
                {
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john.doe@example.com',
                }
            ]
        }
        # Mocking the view context with 'kwargs' attribute
        mock_view = type('', (), {'kwargs': {'pk': self.group.pk}})()
        serializer = ContactListSerializer(data=data, context={'view': mock_view})
        self.assertTrue(serializer.is_valid())

    def test_contact_list_serializer_duplicate_email(self):
        data = {
            'contacts': [
                {
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john.doe@example.com',
                },
                {
                    'first_name': 'Jane',
                    'last_name': 'Doe',
                    'email': 'john.doe@example.com',
                }
            ]
        }
        # Mocking the view context with 'kwargs' attribute
        mock_view = type('', (), {'kwargs': {'pk': self.group.pk}})()
        serializer = ContactListSerializer(data=data, context={'view': mock_view})
        self.assertFalse(serializer.is_valid())
        self.assertIn('contacts', serializer.errors)



        
        
class ProcessEmailsSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='testuser', password='testpass')
        self.group = Group.objects.create(name="Test Group", user=self.user)

    def create_test_csv_file(self, contacts):
        df = pd.DataFrame(contacts)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        df.to_csv(temp_file.name, index=False)
        return temp_file

    def create_test_json_file(self, contacts):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        with open(temp_file.name, 'w') as f:
            json.dump(contacts, f)
        return temp_file

    def test_process_emails_serializer_valid_csv(self):
        contacts = [{'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@example.com'}]
        temp_file = self.create_test_csv_file(contacts)
        with open(temp_file.name, 'rb') as f:
            csv_file = SimpleUploadedFile(temp_file.name, f.read(), content_type='text/csv')
            # Mocking the view context with a mock object that has 'kwargs' attribute
            mock_view = type('', (), {'kwargs': {'pk': self.group.pk}})()
            serializer = ProcessEmailsSerializer(data={'file': csv_file}, context={'view': mock_view})
            self.assertTrue(serializer.is_valid())

    def test_process_emails_serializer_valid_json(self):
        contacts = [{'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@example.com'}]
        temp_file = self.create_test_json_file(contacts)
        with open(temp_file.name, 'rb') as f:
            json_file = SimpleUploadedFile(temp_file.name, f.read(), content_type='application/json')
            # Mocking the view context with a mock object that has 'kwargs' attribute
            mock_view = type('', (), {'kwargs': {'pk': self.group.pk}})()
            serializer = ProcessEmailsSerializer(data={'file': json_file}, context={'view': mock_view})
            self.assertTrue(serializer.is_valid())

    def test_process_emails_serializer_invalid_file_format(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        with open(temp_file.name, 'w') as f:
            f.write("Invalid file content")
        with open(temp_file.name, 'rb') as f:
            invalid_file = SimpleUploadedFile(temp_file.name, f.read(), content_type='text/plain')
            # Mocking the view context with a mock object that has 'kwargs' attribute
            mock_view = type('', (), {'kwargs': {'pk': self.group.pk}})()
            serializer = ProcessEmailsSerializer(data={'file': invalid_file}, context={'view': mock_view})
            self.assertFalse(serializer.is_valid())
            self.assertIn('file', serializer.errors)