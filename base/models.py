from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Opravilo(models.Model):
    uporabnik = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    naslov = models.CharField(max_length=50, null=True, blank=True)
    opis = models.TextField(null=True, blank=True)
    opravljeno = models.BooleanField(default=False)
    ustvarjeno = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.naslov

