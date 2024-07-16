from rest_framework import serializers
from .models import Group, Contact
from django.shortcuts import get_object_or_404
import pandas as pd
from .utilis import generate_error

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ('group','is_subscribed','is_valid')
        
    def validate_email(self,value):
        value = value.lower().strip()
        return value

class ContactListSerializer(serializers.Serializer):
    contacts = serializers.ListField(child=ContactSerializer())

    def validate_contacts(self, contacts_data):
        """
        Validate each contact data in the list and check for duplicates.
        """
        errors = []
        
        group_id = self.context['view'].kwargs.get('pk')
        group = get_object_or_404(Group, id=group_id)

        for index, contact_data in enumerate(contacts_data):
            serializer = ContactSerializer(data=contact_data)

            # Validate individual contact data
            if not serializer.is_valid():
                errors.append({
                    'index': index,
                    'errors': serializer.errors
                })
            else:
                validated_data = serializer.validated_data
                email = validated_data.get('email')

                # Check for duplicate emails within the list
                if any(contact_data['email'] == validated_data['email'] for contact_data in contacts_data[:index]):
                    errors.append({
                        'index': index,
                        'errors': {'email': ['Duplicate email found earlier in the list.']}
                    })

                # Check if the email already exists in the same group
                if Contact.objects.filter(email=email, group=group).exists():
                    errors.append(generate_error(index, email, f'This email "{email}" already exists in the same group.'))

        if errors:
            raise serializers.ValidationError(errors)

        return contacts_data

class ProcessEmailsSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        """
        Validate the uploaded file and extract contact data.
        """
        file_extension = value.name.split('.')[-1].lower()
        if file_extension not in ['csv', 'json']:
            raise serializers.ValidationError('Unsupported file format')

        try:
            if file_extension == 'csv':
                df = pd.read_csv(value)
            elif file_extension == 'json':
                df = pd.read_json(value)
        except Exception as e:
            raise serializers.ValidationError('Error processing file')

        field_mapping = {
            'email': 'email',
            'first name': 'first_name',
            'firstname': 'first_name',
            'first_name': 'first_name',
            'last name': 'last_name',
            'lastname': 'last_name',
            'last_name': 'last_name',
        }

        detected_fields = {}
        for column in df.columns:
            normalized_column = column.lower().replace(' ', '_')
            if normalized_column in field_mapping:
                detected_fields[field_mapping[normalized_column]] = column

        if 'email' not in detected_fields:
            raise serializers.ValidationError('Email field is required in the file')

        contacts = []
        errors = []
        group_id = self.context['view'].kwargs.get('pk')
        group = get_object_or_404(Group, id=group_id)

        for index, row in df.iterrows():
            contact_data = {model_field: row[detected_column] for model_field, detected_column in detected_fields.items()}
            contact_data['group'] = group.id

            # Validate email in contact data
            contact_serializer = ContactSerializer(data=contact_data)
            if not contact_serializer.is_valid():
                errors.append(generate_error(index, contact_data['email'], contact_serializer.errors))
            else:
                email = contact_data['email'].lower().strip()
                contact_data['email'] = email

                # Check for duplicate emails within the list
                if any(c['email'] == email for c in contacts):
                    errors.append(generate_error(index, email, {'email': ['Duplicate email found earlier in the list.']}))

                # Check if the email already exists in the same group
                if Contact.objects.filter(email=email, group=group).exists():
                    errors.append(generate_error(index, email, {'email': [f'This email "{email}" already exists in the same group.']}))
                
                contacts.append(contact_data)

        if errors:
            raise serializers.ValidationError({'errors': errors})
        print(contacts)
        return contacts


class GroupSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = '__all__'
        read_only_fields = ('user',)
        
        
        
        

