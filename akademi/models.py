from django.db import models
from django.conf import settings  # Kullanıcı bilgisi için
from django.contrib.auth.models import User  # Kullanıcı bilgisi için

class Sozluk(models.Model):
    terim = models.CharField(max_length=50, unique=True)  # Örn: RSI, EMA

    ekleyen = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    eklenme_tarihi = models.DateTimeField(auto_now_add=True)
    onayli = models.BooleanField(default=False)

    def __str__(self):
        return self.terim

class SozlukDil(models.Model):
    sozluk = models.ForeignKey(Sozluk, on_delete=models.CASCADE, related_name='ceviriler')
    dil = models.CharField(max_length=10)  # Örn: 'tr', 'en', 'de'
    baslik = models.CharField(max_length=200)
    tanim = models.TextField()
    kategori = models.CharField(max_length=100, blank=True, null=True)
    ornek = models.TextField(blank=True, null=True)
    ekleyen = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    eklenme_tarihi = models.DateTimeField(auto_now_add=True)
    onayli = models.BooleanField(default=False)

    class Meta:
        unique_together = ('sozluk', 'dil')

    def __str__(self):
        return f"{self.sozluk.terim} ({self.dil})"
