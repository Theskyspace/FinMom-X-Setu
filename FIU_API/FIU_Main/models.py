from django.db import models
from django.contrib.auth.models import User

class Consent(models.Model):
    user = models.OneToOneField(User, null = True , on_delete = models.CASCADE , blank = True)
    ConsentHandle = models.TextField(default = "")
    ConsentID = models.TextField(default = "")
    consent_obj = models.TextField(default = "")

    def __str__(self):
        return str(self.user)