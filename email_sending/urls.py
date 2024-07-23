from .views import EmailTemplateDetailView, EmailTemplatesListCreateApiView,SendMailNowView
from django.urls import path


urlpatterns = [
    path('',EmailTemplatesListCreateApiView.as_view()),
    path('email-templates/<int:pk>/', EmailTemplateDetailView.as_view(), name='email-template-detail'),
    path("send/", SendMailNowView.as_view()),
]
