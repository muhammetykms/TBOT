from django.db import models
import ta
import talib


class Indikatorler(models.Model):
    KUTUPHANE_CHOICES = [
        ('ta', 'TA'),
        ('ta-lib', 'TA-Lib'),
        ('custom', 'Custom'),
    ]
    INDIKATOR_GRUBU = [
        ('trend', 'Trend'),
        ('momentum', 'Momentum'),
        ('oynaklik', 'Oynaklık'),
        ('hacim', 'Hacim'),
        ('custom', 'Custom'),
    ]
    adi = models.CharField(max_length=255, unique=True)  # Örn: RSI, Bollinger Bands
    kutuphane = models.CharField(max_length=10, choices=KUTUPHANE_CHOICES, default='custom')  # Hangi kütüphane?
    indikator_grubu = models.CharField(max_length=255, choices=INDIKATOR_GRUBU, default='custom')
    aktif_mi = models.BooleanField(default=True)  # İndikatörün aktif olup olmadığını belirtir
    aciklama = models.TextField(null=True, blank=True)  # İndikatör hakkında açıklama
    kullanim_aciklamasi = models.TextField(null=True, blank=True)
    indikator_ciftleri = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.adi} ({self.kutuphane})"


class IndikatorParametreleri(models.Model):
    indikator_adi = models.CharField(max_length=255,null=True,blank=True)  # Örn: "rsi", "bollinger"
    indikator = models.ForeignKey(Indikatorler, on_delete=models.CASCADE, related_name="parametreler")
    parametre_adi = models.CharField(max_length=255)  # Örn: "window", "short_period"
    varsayilan_deger = models.CharField(null=True, blank=True)  # Varsayılan değer (opsiyonel)
    aciklama = models.TextField(null=True, blank=True)  # Parametre hakkında bilgi
    paramatre_tipi = models.CharField(max_length=255, null=True, blank=True)  # Parametre tipi (örn: int, float, str)
    
    def __str__(self):
        return f"{self.parametre_adi} (Indikator: {self.indikator.adi})"


class IndikatorCiktilari(models.Model):
    indikator_adi = models.CharField(max_length=255,null=True,blank=True)  # Örn: "rsi", "bollinger"
    indikator = models.ForeignKey(Indikatorler, on_delete=models.CASCADE, related_name="ciktilar")
    cikti_adi = models.CharField(max_length=255)  # Örn: "rsi", "bollinger_upper"
    cikti_kodu = models.CharField(max_length=255)  # Örn: "rsi", "bollinger_upper"
    aciklama = models.TextField(null=True, blank=True)  # Çıktı hakkında bilgi

    def __str__(self):
        return f"{self.cikti_adi} (Indikator: {self.indikator.adi})"
