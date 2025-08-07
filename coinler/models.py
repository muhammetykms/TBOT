from django.db import models

# Create your models here.

class Coinler(models.Model):
    name = models.CharField(max_length=50)  # Coin adı (örneğin: Bitcoin)
    sembol = models.CharField(max_length=10)  # Coin sembolü (örneğin: BTC)
    fiyat = models.DecimalField(max_digits=20, decimal_places=8,null=True,blank=True)  # Güncel fiyat
    toplam_piyasa_degeri = models.BigIntegerField(null=True,blank=True)  # Top Piyasa değeri market cap
    volume_1h = models.BigIntegerField(null=True,blank=True)  # son 1 saatlik işlem hacmi
    volume_24h = models.BigIntegerField(null=True,blank=True)  # 24 saatlik işlem hacmi
    dolasimdaki_arz = models.BigIntegerField(null=True,blank=True)  # Dolaşımdaki arz                       --- circulating supply
    toplam_arz = models.BigIntegerField(null=True,blank=True)  # Şu ana kadar üretilmiş toplam coin sayısı  --- total supply
    max_arz = models.BigIntegerField(null=True, blank=True)  # Üretilebilecek en üst sınır (sınırlıysa)     --- maximum supply
    yuzde_deg_son_1h = models.FloatField(null=True,blank=True)  # Son 1 saatteki yüzde değişim
    yuzde_deg_son_24h = models.FloatField(null=True,blank=True)  # Son 24 saatteki yüzde değişim
    yuzde_deg_son_7d = models.FloatField(null=True,blank=True)  # Son 7 gündeki yüzde değişim
    son_guncelleme = models.DateTimeField(auto_now=True)  # Son güncelleme zamanı

    # Yeni eklenen alanlar
    coin_gif = models.CharField(max_length=50, null=True, blank=True)  # Coin için görsel URL'si veya dosya yolu
    teknolojisi = models.TextField(null=True, blank=True)  # Coinin kullandığı teknoloji (örneğin: Blockchain türü)
    ureten_firma = models.CharField(max_length=100, null=True, blank=True)  # Üreten veya geliştiren firma
    merkeziyetsiz_mi = models.BooleanField(default=True)  # Merkeziyetsiz olup olmadığı
    hakkinda = models.TextField(null=True, blank=True)  # Coin hakkında genel bilgiler
    enflasyonist_mi = models.BooleanField(default=False)  # Enflasyonist olup olmadığı
    resmi_web_sitesi = models.URLField(null=True, blank=True)  # Coinin resmi web sitesi
    whitepaper_url = models.URLField(null=True, blank=True)  # Coinin whitepaper bağlantısı


    class Meta:
        verbose_name = "Coin"
        verbose_name_plural = "Coinler"

    def __str__(self):
        return f"{self.name} ({self.symbol})"
