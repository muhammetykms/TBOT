from django.db import models
from account.models import CustomUser
from destek.models import Operatorler
from simple_history.models import HistoricalRecords
from indikatorler.models import Indikatorler, IndikatorCiktilari, IndikatorParametreleri
from mumlar.models import PariteIntervalMarket
# Stratejiye ait genel bilgileri tutar.F


class StratejiDurumlari(models.TextChoices):
    ALIS_BEKLIYOR = 'ALIS_BEKLIYOR', 'Alış Bekliyor'
    ILK_ALIM_YAPILDI = 'ILK_ALIM_YAPILDI', 'İlk Alım Yapıldı'
    EK_ALIM_YAPILDI = 'EK_ALIM_YAPILDI', 'Ek Alım Yapıldı'
    STANDART_SATIM_YAPILDI = 'STANDART_SATIM_YAPILDI', 'Standart Satım Yapıldı'
    ISTISNA_DURUM_SATIM = 'ISTISNA_DURUM_SATIM', 'İstisnai Durumda Satım'
    AFTER_SELL_BEKLEMEDE = 'AFTER_SELL_BEKLEMEDE', 'Satış Sonrası Beklemede'
    BEKLEME_HATA = 'bekleme_hata', 'Hata Nedeniyle Beklemede'
    KULLANICI_DURDURDU = 'KULLANICI_DURDURDU', 'Kullanıcı Tarafından Durduruldu'
    KAPATILDI = 'KAPATILDI', 'Kapatıldı'

class Strateji(models.Model):
    class BorsaTipleri(models.TextChoices):
        BINANCE = 'binance', 'Binance'
        KUCOIN = 'kucoin', 'KuCoin'
        BYBIT = 'bybit', 'Bybit'
        # İstersen diğer borsaları da ekleriz

    class MarketTipleri(models.TextChoices):
        SPOT = 'spot', 'Spot'
        FUTURES = 'futures', 'Futures'
    
    adi = models.CharField(max_length=100)
    aciklama = models.TextField(blank=True, null=True)
    kullanici = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    aktif_mi = models.BooleanField(default=False)
    sistem_aktif_mi = models.BooleanField(default=True, help_text="Sistemde aktif mi?")
    
    borsa = models.CharField(max_length=20, choices=BorsaTipleri.choices, default=BorsaTipleri.BINANCE)
    cüzdan = models.CharField(max_length=50,default='binance_spot')  # İstersen burada borsa+wallet yaparsın
    parite = models.CharField(max_length=50,default="")  # Örn: BTCUSDT
    market_tipi = models.CharField(max_length=20, choices=MarketTipleri.choices,default=MarketTipleri.SPOT)
    
    maksimum_alis_sayisi = models.IntegerField(default=10)
    parite = models.CharField(max_length=50,default="")  # Örn: BTCUSDT
    
    baslangic_butcesi = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    kalan_butce = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    pozisyon_miktari = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    
    kaldirac = models.IntegerField(default=1)  # YENİ EKLEDİK 🔥
        
    # EKLENECEK: tetikleme limitleri
    maksimum_tetikleme_sayisi = models.IntegerField(default=0)  # 0 = limitsiz
    suanki_tetikleme_sayisi = models.IntegerField(default=0)
    durum = models.CharField(
        max_length=50,
        choices=StratejiDurumlari.choices,
        default=StratejiDurumlari.ALIS_BEKLIYOR
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # history = HistoricalRecords()
    
    def __str__(self):
        return f"{self.adi} ({'Aktif' if self.aktif_mi else 'Pasif'})"

class StratejiAlisOrani(models.Model):
    class AlisTipi(models.TextChoices):
        YUZDE = 'yuzde', 'Yüzde (%)'
        SABIT = 'sabit', 'Sabit Tutar'

    class SabitTipi(models.TextChoices):
        USDT = 'usdt', 'USDT Tutarı'
        COIN = 'coin', 'Coin Miktarı'

    strateji = models.ForeignKey(Strateji, on_delete=models.CASCADE, related_name="alis_oranlari")
    siralama = models.IntegerField()  # 0,1,2,3 gibi alış sırası
    oran = models.DecimalField(max_digits=20, decimal_places=8)  # oran veya sabit değer
    tip = models.CharField(max_length=10, choices=AlisTipi.choices, default=AlisTipi.YUZDE)
    sabit_tip = models.CharField(max_length=10, choices=SabitTipi.choices, blank=True, null=True)

    class Meta:
        ordering = ['siralama']

    def __str__(self):
        return f"{self.strateji.adi} - Alış {self.siralama}: {self.oran} {self.tip}"


class StratejiKosullari(models.Model):
    strateji = models.ForeignKey(
        Strateji, on_delete=models.CASCADE, related_name='kosullar'
    )
    
    ifade = models.TextField(
        help_text="Koşulun ifade olarak tanımlanması. Örneğin, EMA(20) > EMA(50)."
    )
    sira = models.PositiveIntegerField(
        default=0, help_text="Koşulların sıralaması."
    )

    karsilastirma_operator = models.ForeignKey(
        Operatorler,
        on_delete=models.CASCADE,
        related_name="kosullari",
        limit_choices_to={"op_grubu": "karsilastirma"},
        verbose_name="Karşılaştırma Operatörü",
        help_text="Bu koşul için kullanılacak karşılaştırma operatörü. Örn: EQ (Eşittir), LT (Küçüktür), GT (Büyüktür)."
    )

    #   BUY     -   SELL
    islem_operator = models.ForeignKey(
        Operatorler,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="islem_operatorleri",
        limit_choices_to={"op_grubu": "islem"},
        verbose_name="İşlem Operatörü",
        help_text="Bu koşul hangi işlem türü için geçerli? Örn: BUY (Alış), SELL (Satış), HOLD (Bekle)."
    )


    # history = HistoricalRecords()

    def __str__(self):
        return f"{self.strateji.adi} - {self.islem_operator.operator_adi if self.islem_operator else 'Bilinmiyor'} (Koşul: {self.ifade})"

class StratejiKosulIndikator(models.Model):
    """ Strateji koşullarına bağlı olarak kullanılan indikatörleri tutar. """
    
    strateji_kosulu = models.ForeignKey(
        StratejiKosullari, on_delete=models.CASCADE, related_name="kosul_indikatorleri"
    )
    
    indikator = models.ForeignKey(
        Indikatorler, on_delete=models.CASCADE, related_name="indikator_kosullar"
    )
    indikator_ciktisi = models.ForeignKey(
        IndikatorCiktilari, on_delete=models.CASCADE, related_name="indikator_cikti_kosullar"
    )
    
    indikator_sirasi = models.CharField(
        max_length=10,
        choices=[("ilk", "İlk"), ("ikinci", "İkinci")],
        default="ilk",
        verbose_name="İndikatör Sırası",
        help_text="Bu parametrenin ilk veya ikinci indikatöre mi ait olduğunu belirtir."
    )

    # 📌 `PariteIntervalMarket` modeline bağlanıyor
    parite_interval_market = models.ForeignKey(
        PariteIntervalMarket, on_delete=models.CASCADE, related_name="kosul_indikatorleri"
    )
    
    def __str__(self):
        return f"{self.strateji_kosulu.strateji.adi} - {self.indikator.adi} ({self.indikator_sirasi})"

class StratejiKosulParametreleri(models.Model):
    """ İndikatörlerin parametreleri ve kullanıcı değerlerini tutar. """
    
    kosul_indikator = models.ForeignKey(
        StratejiKosulIndikator, on_delete=models.CASCADE, related_name="kosul_parametreleri"
    )
    
    indikator_parametre = models.ForeignKey(
        IndikatorParametreleri, on_delete=models.CASCADE, related_name="strateji_kosul_parametreleri"
    )
    
    kullanici_degeri = models.FloatField(
        null=True, blank=True, help_text="Kullanıcı tarafından belirlenen değer."
    )

    def __str__(self):
        return f"{self.kosul_indikator.indikator.adi} - {self.indikator_parametre.parametre_adi}: {self.kullanici_degeri if self.kullanici_degeri is not None else self.indikator_parametre.varsayilan_deger}"

class StratejiKosulBaglantilari(models.Model):
    kosullar = models.ManyToManyField(
        StratejiKosullari, related_name="baglantilar",
        help_text="Birden fazla koşulu AND veya OR ile bağlamak için kullanılır."
    )

    mantiksal_operator = models.ForeignKey(
        Operatorler,
        on_delete=models.CASCADE,
        limit_choices_to={"op_grubu": "mantiksal"},
        verbose_name="Mantıksal Operatör",
        help_text="Bu koşullar nasıl bağlanacak? Örn: AND, OR."
    )

    def __str__(self):
        return f"{' '.join([k.ifade for k in self.kosullar.all()])} {self.mantiksal_operator.operator_adi}"

class StratejiAksiyonu(models.Model):
    strateji = models.ForeignKey(Strateji, on_delete=models.CASCADE, related_name="aksiyonlar")
    AKSIYON_TEMPLATE_MAPPING = {
        # Spot işlemler
        'buy_market': 'aksiyon_parcalar/buy_market.html',
        'buy_limit': 'aksiyon_parcalar/buy_limit.html',
        # 'buy_fok': 'aksiyon_parcalar/buy_fok.html',
        'sell_market': 'aksiyon_parcalar/sell_market.html',
        'sell_limit': 'aksiyon_parcalar/sell_limit.html',
        # 'sell_fok': 'aksiyon_parcalar/sell_fok.html',
        'cancel_orders_spot': 'aksiyon_parcalar/cancel_orders_spot.html',

        # Futures işlemler
        'open_long': 'aksiyon_parcalar/open_long.html',
        'open_short': 'aksiyon_parcalar/open_short.html',
        'close_long': 'aksiyon_parcalar/close_long.html',
        'close_short': 'aksiyon_parcalar/close_short.html',
        'hedge_open': 'aksiyon_parcalar/hedge_open.html',
        'switch_position': 'aksiyon_parcalar/switch_position.html',
        # 'move_stop': 'aksiyon_parcalar/move_stop.html',
        'cancel_orders_futures': 'aksiyon_parcalar/cancel_orders_futures.html',

        # Ortak işlemler
        # 'tp_limit': 'aksiyon_parcalar/tp_limit.html',
        # 'tp_market': 'aksiyon_parcalar/tp_market.html',
        # 'sl_limit': 'aksiyon_parcalar/sl_limit.html',
        # 'sl_market': 'aksiyon_parcalar/sl_market.html',
        'trailing_stop': 'aksiyon_parcalar/trailing_stop.html',
        # 'set_trail': 'aksiyon_parcalar/set_trail.html',
        # 'step_sell': 'aksiyon_parcalar/step_sell.html',
        # 'step_buy': 'aksiyon_parcalar/step_buy.html',
        # 'close_partial': 'aksiyon_parcalar/close_partial.html',
        'dynamic_size': 'aksiyon_parcalar/dynamic_size.html',

        # Yardımcı işlemler
        'wait': 'aksiyon_parcalar/wait.html',
        # 'wait_for_time': 'aksiyon_parcalar/wait_for_time.html',
        # 'wait_for_signal': 'aksiyon_parcalar/wait_for_signal.html',
        'notify': 'aksiyon_parcalar/notify.html',
    }

    AKSIYON_GRUPLARI = {
        'spot': [
            ('buy_market', 'Al (Market)'),
            ('buy_limit', 'Al (Limit)'),
            # ('buy_fok', 'Al (FOK)'),
            ('sell_market', 'Sat (Market)'),
            ('sell_limit', 'Sat (Limit)'),
            # ('sell_fok', 'Sat (FOK)'),
            ('cancel_orders_spot', 'Mevcut Emirleri İptal Et'),
        ],
        'futures': [
            ('open_long', 'Long Pozisyon Aç'),
            ('open_short', 'Short Pozisyon Aç'),
            ('close_long', 'Long Pozisyon Kapat'),
            ('close_short', 'Short Pozisyon Kapat'),
            ('hedge_open', 'Ters Pozisyon Aç'),
            ('switch_position', 'Pozisyon Yönünü Değiştir'),
            # ('move_stop', 'Stop Seviyesini Taşı'),
            ('cancel_orders_futures', 'Mevcut Emirleri İptal Et'),
        ],
        'ortak': [
            # ('tp_limit', 'Take Profit (Limit)'),
            # ('tp_market', 'Take Profit (Market)'),
            # ('sl_limit', 'Stop Loss (Limit)'),
            # ('sl_market', 'Stop Loss (Market)'),
            ('trailing_stop', 'İz Süren Stop'),
            # ('set_trail', 'İz Sürmeyi Başlat'),
            # ('step_sell', 'Kademeli Satış'),
            # ('step_buy', 'Kademeli Alış'),
            # ('close_partial', 'Pozisyonun Bir Kısmını Kapat'),
            ('dynamic_size', 'Dinamik Alım Miktarı'),
        ],
        'yardimci': [
            ('wait', 'Bekle'),
            # ('wait_for_time', 'Zamana Göre Bekle'),
            # ('wait_for_signal', 'Koşula Göre Bekle'),
            ('notify', 'Bildirim Gönder'),
        ]
    }
    
    AKSIYON_TIPLERI = sum(AKSIYON_GRUPLARI.values(), [])
    
    aksiyon_tipi = models.CharField(
        max_length=30,
        choices=AKSIYON_TIPLERI
    )

    coin = models.CharField(max_length=10, default='USDT')  # İşlem yapılacak ana coin
    miktar = models.DecimalField(max_digits=20, decimal_places=8)
    miktar_tipi = models.CharField(max_length=10, choices=[('yuzde', 'Yüzde'), ('sabit', 'Sabit')], default='yuzde')

    # Emir tipi
    emir_tipi = models.CharField(max_length=20, choices=[
        ('market', 'Market'),
        ('limit', 'Limit'),
        ('fok', 'Fill or Kill'),
        ('ioc', 'Immediate or Cancel'),
    ], default='market')

    limit_fiyat = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)

    # Futures'a özel
    kaldirac = models.PositiveIntegerField(null=True, blank=True)
    pozisyon_yonu = models.CharField(
        max_length=10,
        choices=[('long', 'Long'), ('short', 'Short')],
        null=True,
        blank=True
    )

    reduce_only = models.BooleanField(default=False)  # Pozisyon kapama emirlerinde kullanılır

    # Takip için
    sira = models.PositiveSmallIntegerField(default=0)  # kademeli işlemler için
    olusturulma_zamani = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sira']


class StratejiIstisnalari(models.Model):
    aksiyon = models.ForeignKey(StratejiAksiyonu, on_delete=models.CASCADE, related_name="istisnalar")
    kosul = models.ForeignKey(StratejiKosullari, on_delete=models.CASCADE)
    mantiksal_operator = models.ForeignKey(
        Operatorler,
        on_delete=models.CASCADE,
        limit_choices_to={'op_grubu': 'mantiksal'},
        help_text="Bu koşul aksiyonun yapılmaması için ne şekilde bağlanacak? Örn: AND, OR"
    )

    def __str__(self):
        return f"{self.aksiyon.aksiyon} için istisna: {self.kosul.ifade}"

class StratejiZamanlama(models.Model):
    strateji = models.OneToOneField(
        Strateji,
        on_delete=models.CASCADE,
        related_name="zamanlama"
    )

    baslangic_saati = models.TimeField(
        null=True, blank=True,
        help_text="Strateji bu saatten önce çalışmaz"
    )
    bitis_saati = models.TimeField(
        null=True, blank=True,
        help_text="Strateji bu saatten sonra çalışmaz"
    )

    sadece_hafta_ici = models.BooleanField(
        default=False,
        help_text="Hafta sonları devre dışı bırak"
    )

    aktif_baslangic_tarihi = models.DateField(
        null=True, blank=True,
        help_text="Strateji sadece bu tarihten itibaren aktif olur"
    )
    aktif_bitis_tarihi = models.DateField(
        null=True, blank=True,
        help_text="Bu tarihten sonra strateji devre dışı kalır"
    )

    tekrar_araligi_dakika = models.PositiveIntegerField(
        default=0,
        help_text="Strateji her kaç dakikada bir tetiklensin? (0 = her an kontrol et)"
    )

    def __str__(self):
        return f"{self.strateji.adi} zamanlama"

    def aktif_mi(self, zaman=None):
        """
        Verilen zamana göre bu strateji şu an aktif mi?
        """
        import datetime
        zaman = zaman or datetime.datetime.now()

        if self.aktif_baslangic_tarihi and zaman.date() < self.aktif_baslangic_tarihi:
            return False
        if self.aktif_bitis_tarihi and zaman.date() > self.aktif_bitis_tarihi:
            return False
        if self.sadece_hafta_ici and zaman.weekday() >= 5:
            return False
        if self.baslangic_saati and zaman.time() < self.baslangic_saati:
            return False
        if self.bitis_saati and zaman.time() > self.bitis_saati:
            return False
        return True

class StratejiBeklemeKosulu(models.Model):
    strateji = models.ForeignKey(Strateji, on_delete=models.CASCADE, related_name="bekleme_kosullari")
    kosul = models.ForeignKey(StratejiKosullari, on_delete=models.CASCADE)
    bitis_kosulu = models.ForeignKey(StratejiKosullari, on_delete=models.CASCADE, related_name="bitiren_kosul")
    aciklama = models.TextField(null=True, blank=True)

class AcikIslem(models.Model):
    strateji = models.ForeignKey(Strateji, on_delete=models.CASCADE)
    coin = models.CharField(max_length=20)
    ilk_alis_fiyati = models.FloatField()
    ortalama_fiyat = models.FloatField()
    toplam_maliyet = models.FloatField()
    toplam_adet = models.FloatField()
    tekrar_sayisi = models.IntegerField(default=1)
    acilis_zamani = models.DateTimeField(auto_now_add=True)
    son_islem_zamani = models.DateTimeField(auto_now=True)
    aktif_mi = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.strateji.adi} - {self.coin} - {self.toplam_adet:.4f} adet @ {self.ortalama_fiyat:.2f} USDT"

class IslemAdimi(models.Model):
    acik_islem = models.ForeignKey(AcikIslem, on_delete=models.CASCADE, related_name="islem_adimlari")
    islem_tipi = models.CharField(max_length=10, choices=[('AL', 'Al'), ('SAT', 'Sat')])
    miktar = models.FloatField(help_text="Adet cinsinden")
    birim_fiyat = models.FloatField(help_text="USDT cinsinden fiyat")
    toplam_usdt = models.FloatField(help_text="Toplam işlem değeri = miktar * birim fiyat")
    islem_zamani = models.DateTimeField(auto_now_add=True)
    parite = models.CharField(max_length=20, help_text="İşlem yapılan parite, örn: BNBUSDT")
    emir_tipi = models.CharField(max_length=10, choices=[('limit', 'Limit'), ('market', 'Market')], default='market')

    def __str__(self):
        return f"{self.islem_tipi} {self.miktar} @ {self.birim_fiyat} on {self.parite}"

    def guncelle(self):
        adimlar = self.islem_adimlari.filter(islem_tipi='AL')
        toplam_usdt = sum([a.toplam_usdt for a in adimlar])
        toplam_adet = sum([a.miktar for a in adimlar])
        self.toplam_maliyet = toplam_usdt
        self.toplam_adet = toplam_adet
        self.ortalama_fiyat = toplam_usdt / toplam_adet if toplam_adet else 0
        self.tekrar_sayisi = adimlar.count()
        self.save()



"""

[ STRATEJİ ADI + AÇIKLAMA ]
    ↓

--- IF GRUBU 1 ---
[ RSI(14) < 30 ]      [ timeframe: 4h ]
[ MFI(14) < 20 ]      [ timeframe: 4h ]
[ bağlaç: AND ]
    ↓

--- THEN GRUBU 1 ---
[ BUY 10% BNB with USDT as LIMIT ]

    ↓

--- AND THEN ---
[ Fiyat %5 artarsa → TRAILING STOP başlat ]

--- OR ---
[ RSI > 70 OR MACD > 0 ] 
    ↓

--- THEN GRUBU 2 ---
[ SELL 100% BNB ]

--- DO NOT ---
[ RSI < 50 ise satma ]





🔧 4. BUNU SİSTEMSEL OLARAK NASIL MODELLİYORUZ?

Her grup:
Grup Türü	    Model
IF bloğu	    StratejiKosullari + StratejiKosulBaglantilari
THEN bloğu	    StratejiAksiyonu
Bağlaç	        mantiksal_operator alanı (AND, OR)
THEN’in sırası	StratejiAksiyonu (sıralı sira alanıyla)
DO NOT bloğu	StratejiIstisnalari
WAIT UNTIL	    StratejiBeklemeKosulu (önerilen)

Bu yapılarla tek sayfada sınırsız şart–aksiyon–istisna zinciri kurabilirsin ✅




"""





# SENİN MEVCUT MODELLERİNLE İLİŞKİLENDİRELİM

#     StratejiKosullari – tekil koşul
#     StratejiKosulBaglantilari – mantıksal bağlayıcı (AND, OR)
#     StratejiAksiyonu – THEN / AND THEN karşılığı
#     StratejiIstisnalari – DO NOT karşılığı (yeni önerdik)
#     StratejiZamanlama – ANY TIME / ZAMAN BLOĞU karşılığı


