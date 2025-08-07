from django.db import models


class Interval(models.Model):
    INTERVAL_CHOICES = [
        ('1m', '1 Dakikalık'),
        ('5m', '5 Dakikalık'),
        ('15m', '15 Dakikalık'),
        ('30m', '30 Dakikalık'),
        ('1h', '1 Saatlik'),
        ('2h', '2 Saatlik'),
        ('4h', '4 Saatlik'),
        ('1d', '1 Günlük'),
        ('1w', '1 Haftalık'),
    ]

    interval=models.CharField(
        max_length=3,
        choices=INTERVAL_CHOICES)
    onay=models.BooleanField(default=False)
    
    def __str__(self):
        return self.interval
    
    
class MarketType(models.Model):
    MARKET_CHOICES = [
        ('spot', 'Spot'),
        ('futures', 'Futures'),
    ]

    market_type = models.CharField(
        max_length=10,
        choices=MARKET_CHOICES
    )

    def __str__(self):
        return self.market_type
    
    
# Create your models here.
class Pariteler(models.Model):
    PARITE_TIPI = [
        ('parite', 'Normal Parite'),
        ('endeks', 'Endeks / Gösterge'),  # Örn: BTC.D, TOTAL
    ]
    pariteler=models.CharField(max_length=50,unique=True)
    base = models.CharField(max_length=20, blank=True, null=True)   # Alınan coin
    quote = models.CharField(max_length=20, blank=True, null=True)  # Ödeme yapılan coin
    tip = models.CharField(max_length=10, choices=PARITE_TIPI, default='parite')
    onay=models.BooleanField(default=True)

    def __str__(self):
        return self.pariteler


class PariteIntervalMarket(models.Model):
    parite = models.ForeignKey(Pariteler, on_delete=models.CASCADE)
    interval = models.ForeignKey(Interval, on_delete=models.CASCADE)
    market = models.ForeignKey(MarketType, on_delete=models.CASCADE,null=True, blank=True)
    onay = models.BooleanField(default=True)  # Ek alan (isteğe bağlı)
    
    class Meta:
        unique_together = ('parite', 'interval', 'market')  # Aynı kombinasyonu tekrarlamayı engeller

    def __str__(self):
        return f"{self.parite} - {self.interval} - {self.market}"

"""
ÖNEMLİ NOT:

Bu sistem şuan için sadece adminin hizmetinde eğer başka kullanıcılar içinde olacaksa 
KullaniciPariteIntervalMarket adında bir model oluşturulup bu modelde kullanıcıya özel parite-interval-market bilgileri tutulabilir.
Bu modeldeki onay alanına göre pariteler işlemden geri çekilir vb.



"""
