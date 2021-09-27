from django.db import models
from django.contrib.auth.models import User

class Consent(models.Model):
    user = models.OneToOneField(User, null = True , on_delete = models.CASCADE , blank = True)
    Consent_ID = models.TextField()

    def __str__(self):
        return str(self.user)