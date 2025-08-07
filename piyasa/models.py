from django.db import models

# Create your models here.
from django.db import models

class PiyasaOzeti(models.Model):
    tarih = models.DateField(auto_now_add=True)
    artan_coin_sayisi = models.IntegerField()
    dusen_coin_sayisi = models.IntegerField()
    ortalama_volatilite = models.FloatField()
    toplam_hacim = models.FloatField()
    btc_dominans = models.FloatField()
    yorum = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tarih} - Özeti"
