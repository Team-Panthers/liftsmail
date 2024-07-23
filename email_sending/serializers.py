from .models import EmailTemplate, EmailSession
from rest_framework import serializers


class EmailTemplatesSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        exclude = ['user']
        


class SendMailNowSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSession
        fields = ['session', 'group_id', 'template_id', 'is_scheduled']


class ScheduleMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSession
        fields = ['session', 'group_id', 'template_id', 'is_scheduled', 'schedule_time']