from .views import EmailTemplateDetailView, EmailTemplatesListCreateApiView,SendMailNowView, EmailSessionView, ScheduleMailView
from django.urls import path


urlpatterns = [
    path('',EmailTemplatesListCreateApiView.as_view()),
    
    path('email_templates/<int:pk>/', EmailTemplateDetailView.as_view(), name='email-template-detail'),
    
    path('send_now/', SendMailNowView.as_view(), name='send-now'),

    path('schedule/', ScheduleMailView.as_view(), name='schedule-mail'),

    path('sessions/', EmailSessionView.as_view(), name="email-session"),
]
