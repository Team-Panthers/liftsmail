from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from  emails.models import Group
from .permissions import IsOwner



class EmailProcessMixin:
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = []
    def create(self, request, *args, **kwargs):
        print(request.user)
        group = self.get_object()
        self.check_object_permissions(request, group)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": f"Processed and added contacts to group {group.id}"}, status=status.HTTP_201_CREATED)
    
    def get_object(self):
        group_id = self.kwargs.get('pk')
        group = get_object_or_404(Group, id=group_id)
        return group