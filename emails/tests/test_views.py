import os
import tempfile
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from emails.models import Group, Contact
import io
import csv
import json
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

def create_contacts_csv(contacts):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['first_name', 'last_name', 'email'])
    for contact in contacts:
        writer.writerow([contact['first_name'], contact['last_name'], contact['email']])
    output.seek(0)
    return output

def create_contacts_json_file(contacts):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    with open(temp_file.name, 'w') as f:
        json.dump(contacts, f)
    return temp_file

class ContactGroupTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuse@gmail.com', password='testpass')
        self.client.force_authenticate(self.user)
        self.group = Group.objects.create(name="Test Group", user=self.user)
        self.contact_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
        }

    def tearDown(self):
        # Cleanup any temporary files created
        temp_files = [f for f in os.listdir(tempfile.gettempdir()) if f.endswith('.json')]
        for f in temp_files:
            os.remove(os.path.join(tempfile.gettempdir(), f))

    def test_create_group(self):
        url = reverse('group-list-create')
        data = {'name': 'New Group'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 2)
        self.assertEqual(Group.objects.get(id=response.data['id']).name, 'New Group')

    def test_add_contact_to_group(self):
        url = reverse('contact-list-create', kwargs={'pk': self.group.id})
        response = self.client.post(url, self.contact_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(Contact.objects.get(id=response.data['id']).email, 'john.doe@example.com')

    def test_add_duplicate_contact_to_group(self):
        Contact.objects.create(group=self.group, **self.contact_data)
        url = reverse('contact-list-create', kwargs={'pk': self.group.id})
        response = self.client.post(url, self.contact_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_group_contacts(self):
        Contact.objects.create(group=self.group, **self.contact_data)
        url = reverse('contact-list-create', kwargs={'pk': self.group.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], 'john.doe@example.com')

    def test_process_emails(self):
        url = reverse('process-emails', kwargs={'pk': self.group.id})
        
        # Test with CSV file
        contacts_csv = create_contacts_csv([self.contact_data])
        contacts_csv_file = SimpleUploadedFile("contacts.csv", contacts_csv.read().encode('utf-8'), content_type="text/csv")
        response_csv = self.client.post(url, {'file': contacts_csv_file}, format='multipart')
        self.assertEqual(response_csv.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(Contact.objects.get(email='john.doe@example.com').first_name, 'John')

        # Test with JSON file
        Contact.objects.all().delete()  # Clear contacts before next test
        contacts_json_file = create_contacts_json_file([self.contact_data])
        with open(contacts_json_file.name, 'rb') as f:
            contacts_json = SimpleUploadedFile("test.json", f.read(), content_type="application/json")
            response_json = self.client.post(url, {'file': contacts_json}, format='multipart')
        self.assertEqual(response_json.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(Contact.objects.get(email='john.doe@example.com').first_name, 'John')

    def test_update_contact(self):
        contact = Contact.objects.create(group=self.group, **self.contact_data)
        url = reverse('contact-detail', kwargs={'group_id': self.group.id, 'pk': contact.id})
        updated_data = {'first_name': 'Jane', 'email': 'john.doe@example.com'}
        response = self.client.put(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contact.refresh_from_db()
        self.assertEqual(contact.first_name, 'Jane')

    def test_delete_contact(self):
        contact = Contact.objects.create(group=self.group, **self.contact_data)
        url = reverse('contact-detail', kwargs={'group_id': self.group.id, 'pk': contact.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Contact.objects.count(), 0)
