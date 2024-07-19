from django.db import models
from django.contrib.auth import get_user_model
from liftsmail.models import TimeStampBaseModel

User = get_user_model()


class EmailTemplate(TimeStampBaseModel):
    name = models.CharField(max_length=50)
    subject = models.CharField(max_length=50)
    body = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name}-{self.user.id}"
    
    class Meta:
        unique_together = ['user',"name"]
