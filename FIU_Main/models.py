from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Consent(models.Model):
    user = models.OneToOneField(User, null = True , on_delete = models.CASCADE , blank = True)
    ConsentHandle = models.TextField(default = "")
    ConsentID = models.TextField(default = "")
    consent_obj = models.TextField(default = "")
    FirstTime = models.BooleanField(default=False)
    Investments = models.FloatField(default = -1)
    Networth = models.FloatField(default = -1)
    Last_Updated = models.DateField()

    
    def __str__(self):
        return str(self.user)