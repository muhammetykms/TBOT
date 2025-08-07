from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from coinler.models import Coinler

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=11, unique=True)
    email = models.CharField(max_length=50)
    tel_no = models.CharField(max_length=15)
    yetkili_mi = models.BooleanField(default=False)
    patron_mu = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    dil_tercihi = models.CharField(max_length=10, default='tr')
    bildirim_tercihi = models.BooleanField(default=True)

class Keys(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='keys')
    api_key = models.CharField(max_length=100)
    secret_key = models.CharField(max_length=100)
    borsa = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username

class KullaniciEmtia(models.Model):
    kullanici = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='emtialar')
    emtia_adi = models.CharField(max_length=20,default='USDT')  # Örn: USDT, BTC
    free = models.DecimalField(max_digits=20, decimal_places=8)  # Serbest bakiye
    locked = models.DecimalField(max_digits=20, decimal_places=8)  # Kilitli bakiye
    borsa = models.CharField(max_length=255,default='binance')
    def __str__(self):
        return f"{self.kullanici.username} - {self.emtia_adi}"
