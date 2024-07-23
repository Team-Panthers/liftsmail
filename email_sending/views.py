from .serializers import EmailTemplatesSerializers, SendMailNowSerializer, ScheduleMailSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import EmailTemplate, EmailSession
from liftsmail.permissions import IsOwner
from emails.models import Group
from rest_framework.response import Response
from .utils import format_email
from email_sending.tasks import send_email_task

class EmailTemplatesListCreateApiView(generics.ListCreateAPIView):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplatesSerializers
    permission_classes = [IsAuthenticated, IsOwner]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)

class EmailTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplatesSerializers
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        # user to ensure that users can only access their own templates
        return EmailTemplate.objects.filter(user=self.request.user)
    

class SendMailNowView(generics.CreateAPIView):
    serializer_class = SendMailNowSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = SendMailNowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group_id = serializer.validated_data['group']
        template_id = serializer.validated_data['template']
        group = Group.objects.get(id= group_id)
        email_template = EmailTemplate.objects.get(id=template_id)

        message = email_template.body
        subject = email_template.subject

        contacts = group.contacts.all()

        for contact in contacts:
            context = {
                "first_name":contact.first_name if contact.first_name else "Guest",
                'last_name':contact.last_name if contact.last_name else "Guest" ,
                'email':contact.email,
                "contact_id":contact.id
            }
            new_message = format_email(message, context)
            send_email_task.delay(message=new_message, subject=subject, recipient=contact.email) #Sent to celery
        return Response({"message": "Emails sent successfully"})


class ScheduleMailView(generics.CreateAPIView):
    serializer_class = ScheduleMailSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = serializer.validated_data['session']
        template_id = serializer.validated_data['template_id']
        group_id = serializer.validated_data['group_id']
        schedule_time = serializer.validated_data['schedule_time']

        email_template = EmailTemplate.objects.get(id=template_id)
        group = Group.objects.get(id=group_id)
        contacts = group.contacts.all()

        for contact in contacts:
            context = {
                "first_name":contact.first_name if contact.first_name else "Guest",
                'last_name':contact.last_name ,
                'email':contact.email,
                "contact_id":contact.id
            }

        subject = email_template.subject
        body = email_template.body