from .views import EmailTemplatesListCreateApiView,SendMail
from django.urls import path


urlpatterns = [
    path('',EmailTemplatesListCreateApiView.as_view()),
    path("send/", SendMail.as_view()),
]
