from .models import EmailTemplate
from rest_framework import serializers


class EmailTemplatesSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        exclude = ['user']
        
        
        
class SendMailSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    template_id = serializers.IntegerField()