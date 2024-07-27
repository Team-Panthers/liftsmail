from emails.models import Group
from .models import EmailTemplate, EmailSession
from rest_framework import serializers


class EmailTemplatesSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        exclude = ['user']

class SimpleEmailTemplatesSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        exclude = ['user', 'name']


class SendNowSerializer(serializers.ModelSerializer):
    template = SimpleEmailTemplatesSerializers() 
    class Meta:
        model = EmailSession
        fields = ['id', 'user', 'session', 'group_id', 'template']
        read_only_fields = ('user',)

    def __init__(self, *args, **kwargs):
        super(SendNowSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            user = request.user
            self.fields['group_id'].queryset = Group.objects.filter(user=user)


class SendMailNowSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSession
        fields = ['id', 'user', 'session', 'group_id', 'template_id', 'is_scheduled']
        read_only_fields = ('user',)

    def __init__(self, *args, **kwargs):
        super(SendMailNowSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            user = request.user
            self.fields['group_id'].queryset = Group.objects.filter(user=user)
            self.fields['template_id'].queryset = EmailTemplate.objects.filter(user=user)


class ScheduleMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSession
        fields = ['session', 'group_id', 'template_id', 'is_scheduled', 'schedule_time']

    def __init__(self, *args, **kwargs):
        super(ScheduleMailSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            user = request.user
            self.fields['group_id'].queryset = Group.objects.filter(user=user)
            self.fields['template_id'].queryset = EmailTemplate.objects.filter(user=user)


class EmailSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSession
        fields = '__all__'