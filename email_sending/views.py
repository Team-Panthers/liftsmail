from .serializers import EmailTemplatesSerializers,SendMailSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import EmailTemplate
from liftsmail.permissions import IsOwner
from emails.models import Group
from django.template.loader import render_to_string
from rest_framework.response import Response


class EmailTemplatesListCreateApiView(generics.ListCreateAPIView):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplatesSerializers
    permission_classes = [IsAuthenticated,IsOwner]
    
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)
    
    
class SendMail(generics.CreateAPIView):
    serializer_class = SendMailSerializer
    queryset = []
    # user prodviude the group hen wannt to send and also the email template to used
    def post(self,request,*args, **kwargs):
        serializer = SendMailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group_id = serializer.validated_data['group_id']
        template_id = serializer.validated_data['template_id']
        
        group = Group.objects.get(id= group_id)
        email_template = EmailTemplate.objects.get(id=template_id)
        
        
        message = email_template.body
        subject = email_template.subject
        
        contacts = group.contacts.all()
        
        
        
        for contact in contacts:
            context = {
                "first_name":contact.first_name if contact.first_name else "Guest",
                'last_name':contact.last_name ,
                'email':contact.email,
                "contact_id":contact.id
            }
            new_message = format_email(message,context)
            
            print(new_message)
            
            
            # send(messge=new_message,subject=subject,email=contact.email)
            
        return Response({"message":new_message})
        
        
        
        
      
      
      
import os
from django.template.loader import render_to_string
import tempfile
import random
import string
      
        
def format_email(message, context):
    """
    Renders the email template content with the given context.
    
    Args:
        message (str): The email message content.
        context (dict): The context data to render the template.
    
    Returns:
        str: The rendered email content.
    """
    # Generate a unique filename
    contact_id = context.get('contact_id')
    filename = generate_html_file_name(contact_id)
    
    # Create a temporary file
    temp_file_path = os.path.join('templates', filename)
    
    try:
        # Write the message content to the temporary file
        with open(temp_file_path, 'w') as file:
            file.write(message)
        
        # Render the template with context
        rendered_content = render_to_string(filename, context)
        print(rendered_content)
    
    finally:
        # Remove the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    
    return rendered_content


def generate_html_file_name(identifier):
    """
    Generates a unique filename based on the given identifier and a random 15-character alphanumeric string.
    
    Args:
        identifier (str): The identifier to use in the filename.
    
    Returns:
        str: The generated filename with a random 15-character string.
    """
    # Generate a random 15-character alphanumeric string
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
    
    # Combine the identifier and random string to create the filename
    return f"emailtemplate_{identifier}_{random_string}.html"
        