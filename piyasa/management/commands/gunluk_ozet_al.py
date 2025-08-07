from django.core.management.base import BaseCommand
from piyasa.services import PiyasaServisi
from piyasa.models import PiyasaOzeti

# celebry yada benzer birşeyle hergün otomatik çalıştırılacak bir komut yazmak için aşağıdaki kodu kullanabilirsiniz. Bu kod, piyasa özetini hesaplar ve veritabanına kaydeder. Bu kodu kullanabilmek için öncelikle piyasa/models.py dosyasına aşağıdaki modeli eklemeniz gerekmektedir:
# ```python
# from django.db import models


class Command(BaseCommand):
    help = "Günlük piyasa özetini hesaplar ve veritabanına kaydeder"

    def handle(self, *args, **kwargs):
        df = PiyasaServisi.binance_tum_coinleri_al()
        oz = PiyasaServisi.piyasa_ozeti(df)
        dominans = PiyasaServisi.btc_dominans()
        yorum = PiyasaServisi.otomatik_yorum(df)

        PiyasaOzeti.objects.create(
            artan_coin_sayisi=oz['artan_sayi'],
            dusen_coin_sayisi=oz['dusen_sayi'],
            ortalama_volatilite=oz['ortalama_volatilite'],
            toplam_hacim=oz['toplam_hacim'],
            btc_dominans=dominans,
            yorum=yorum
        )
        self.stdout.write(self.style.SUCCESS("Piyasa özeti başarıyla kaydedildi."))
