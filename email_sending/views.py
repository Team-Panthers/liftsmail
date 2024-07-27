import json
from .serializers import EmailTemplatesSerializers, ScheduleMailSerializer, EmailSessionSerializer, SendNowSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import EmailTemplate, EmailSession
from liftsmail.permissions import IsOwner
from emails.models import Group
from rest_framework.response import Response
from .utils import format_email, send_email
from email_sending.tasks import send_email_task
from django_celery_beat.models import PeriodicTask, CrontabSchedule

class EmailTemplatesListCreateApiView(generics.ListCreateAPIView):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplatesSerializers
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return  EmailTemplate.objects.filter(user=self.request.user)

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
    serializer_class = SendNowSerializer
    permission_classes = [IsAuthenticated]
    queryset = EmailSession.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        template = serializer.validated_data['template']
        group = serializer.validated_data['group_id']

        message = template.body
        subject = template.subject

        contacts = group.contacts.all()

        if not contacts:
            return Response({"detail": "This group has no contacts"}, status=400)
        
        for contact in contacts:
            context = {
                "first_name": contact.first_name if contact.first_name else "Guest",
                'last_name': contact.last_name if contact.last_name else "Guest",
                'email': contact.email,
                "contact_id": contact.id
            }
            new_message = format_email(message, context)
            send_email_task.delay(message=new_message, subject=subject, recipient=contact.email)
        
        return Response({"message": "Emails sent successfully"})

class ScheduleMailView(generics.CreateAPIView):
    serializer_class = ScheduleMailSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email_template = serializer.validated_data['template_id']
        group = serializer.validated_data['group_id']
        is_scheduled = serializer.validated_data['is_scheduled']
        schedule_time = serializer.validated_data['schedule_time']

        contacts = group.contacts.all()

        if not contacts:
            return Response({"detail": "This group has no contacts"}, status=400)

        subject = email_template.subject
        message = email_template.body

        for contact in contacts:
            context = {
                "first_name": contact.first_name if contact.first_name else "Guest",
                'last_name': contact.last_name if contact.last_name else "Guest",
                'email': contact.email,
                "contact_id": contact.id
            }
            new_message = format_email(message, context)

            if is_scheduled:
                schedule, created = CrontabSchedule.objects.get_or_create(
                    minute=schedule_time.minute,
                    hour=schedule_time.hour,
                    day_of_month=schedule_time.day,
                    month_of_year=schedule_time.month,
                    day_of_week=schedule_time.strftime('%w')
                )
                PeriodicTask.objects.create(
                    crontab=schedule,
                    name=f'send-email-{contact.id}-{schedule_time}',
                    task='email_sending.tasks.send_email_task',
                    args=json.dumps([new_message, subject, contact.email]),
                )
            else:
                send_email_task.delay(message=new_message, subject=subject, recipient=contact.email)

        return Response({"message": "Emails scheduled" if is_scheduled else "Emails sent successfully"})


class EmailSessionView(generics.ListAPIView):
    queryset  = EmailSession.objects.all()
    serializer_class = EmailSessionSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return EmailSession.objects.filter(user=self.request.user)