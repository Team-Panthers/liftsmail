import logging
import logging

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly

from .models import Group, Contact
from liftsmail.mixins import EmailProcessMixin
from .serializers import GroupSerializer, ContactSerializer, ContactListSerializer,ProcessEmailsSerializer
from liftsmail.permissions import IsOwner
import pandas as pd


logger = logging.getLogger(__name__)



class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def get_queryset(self):
        context =  super().get_queryset()
        return context.filter(user=self.request.user)


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsOwner]


class AddContactsView(EmailProcessMixin,generics.CreateAPIView):
    serializer_class = ContactListSerializer

    def perform_create(self, serializer):
        group = self.get_object()

        contacts = serializer.validated_data.get('contacts', [])
        try:
            with transaction.atomic():
                for contact_data in contacts:
                    contact_serializer = ContactSerializer(data=contact_data)
                    if contact_serializer.is_valid():
                        contact_serializer.save(group=group)
                    else:
                        raise ValueError(contact_serializer.errors)
            logger.info(f"Added contacts to group {group.id}")
        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
            raise serializers.ValidationError(str(ve))
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise serializers.ValidationError("An unexpected error occurred. Please try again later.")


class ProcessEmailsView(EmailProcessMixin,generics.CreateAPIView):
    serializer_class = ProcessEmailsSerializer

    def perform_create(self, serializer):
        group = self.get_object()
        contacts = serializer.validated_data.get("file",[])
        try:
            with transaction.atomic():
                for contact_data in contacts:
                    email = contact_data['email']
                    existing_contact = Contact.objects.filter(email=email, group=group).first()
                    if existing_contact:
                        for key, value in contact_data.items():
                            setattr(existing_contact, key, value)
                        existing_contact.save()
                    else:
                        contact_serializer = ContactSerializer(data=contact_data)
                        if contact_serializer.is_valid():
                            contact_serializer.save(group=group)
                        else:
                            raise ValueError(contact_serializer.errors)
            logger.info(f"Processed and added contacts to group {group.id}")
            return Response({"message":f"Processed and added contacts to group {group.id}"})
        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
            raise serializers.ValidationError(str(ve))
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise serializers.ValidationError("An unexpected error occurred. Please try again later.")
        


class ContactListCreateView(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    
    def get_group(self):
        group_id = self.kwargs['pk']
        group = get_object_or_404(Group, id=group_id)
        self.check_object_permissions(self.request, group)
        return group
    
    def get_queryset(self):
        group = self.get_group()
        return Contact.objects.filter(group=group)

    def perform_create(self, serializer):
        group = self.get_group()
        email = serializer.validated_data['email']
    
        existing_contact = Contact.objects.filter(email=email, group=group).first()
        if existing_contact:
            raise serializers.ValidationError({'email': ['Contact with this email already exists in the group.']})
        
        serializer.save(group=group)

class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    
    def get_object(self):
        group_id = self.kwargs['group_id']
        contact_id = self.kwargs['pk']
        group = get_object_or_404(Group, id=group_id)
        self.check_object_permissions(self.request, group)
        contact = get_object_or_404(Contact, id=contact_id, group=group)
        return contact
