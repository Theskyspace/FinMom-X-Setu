from django.db import models
from django.contrib.auth.models import User

class Consent(models.Model):
    user = models.OneToOneField(User, null = True , on_delete = models.CASCADE)
    Consent_ID = models.TextField()

    def __str__(self):
        return self.user