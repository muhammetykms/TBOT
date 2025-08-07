from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.template.loader import render_to_string
from tbotmumarayuz.decorators import check_user_authenticated

from .models import (Strateji, StratejiKosullari, StratejiKosulIndikator, 
    StratejiKosulParametreleri, StratejiKosulBaglantilari)
from indikatorler.models import Indikatorler, IndikatorParametreleri, IndikatorCiktilari

from destek.models import Operatorler
from mumlar.models import PariteIntervalMarket, Pariteler

from pprint import pprint
import json
import uuid

# Create your views here.

from mumlar.models import MarketType  # Model mumlar app'inden geliyor

from itertools import chain
from .models import StratejiAksiyonu
from destek.models import Operatorler


# bloklar/base.py
from django.template.loader import render_to_string

class BaseBlok:
    def __init__(self, request):
        self.request = request
        self.caller = request.GET.get("caller", "default")
        self.strateji_id = request.GET.get("strateji_id")
        self.surec = request.GET.get("surec")
        self.parent_id = request.GET.get("blok_id")
        self.blok_id = f"{self.yeni_uuid_uret()}"

    def yeni_uuid_uret(self):
        import uuid
        return uuid.uuid4().hex[:4]

    def icerik_verilerini_getir(self):
        raise NotImplementedError()

    def sablon_adini_getir(self):
        raise NotImplementedError("Bu sınıf sablon_adini_getir() metodunu override etmelidir.")

    def render(self):
        return render_to_string(self.sablon_adini_getir(), self.icerik_verilerini_getir())

class IfBlok(BaseBlok):
    def sablon_adini_getir(self):
        return 'stratejiler/parcalar/if_blogu_partial.html'

    def icerik_verilerini_getir(self):
        strateji = get_object_or_404(Strateji, id=self.strateji_id, kullanici=self.request.user)
        market_tipi = strateji.market_tipi

        pariteler = PariteIntervalMarket.objects.filter(
            onay=True,
            market_id=1 if market_tipi == "spot" else 2,
            parite__tip="parite"
        )
        endeksler = PariteIntervalMarket.objects.filter(
            onay=True,
            parite__tip="endeks"
        )

        parite_interval_market = list(chain(pariteler, endeksler))

        indikatorler = Indikatorler.objects.filter(aktif_mi=True)
        indikator_listesi = []
        for indikator in indikatorler:
            parametreler = list(IndikatorParametreleri.objects.filter(indikator=indikator))
            ciktilar = list(IndikatorCiktilari.objects.filter(indikator=indikator))
            indikator_listesi.append({
                'indikator': indikator,
                'parametreler': parametreler,
                'ciktilar': ciktilar,
            })

        
        if self.caller == "ve_if":
            state_ekleme_acikmi = True
        elif self.caller == "state_if":
            state_ekleme_acikmi = False
        elif self.caller == "aksiyon_if":
            state_ekleme_acikmi = False
        elif self.caller == "proses_if":
            state_ekleme_acikmi = False
        else:
            state_ekleme_acikmi = False

        return {
            'parite_interval_market': parite_interval_market,
            'indikator_listesi': indikator_listesi,
            'blok_id': self.blok_id,
            'parent_id': self.parent_id,
            'strateji_id': self.strateji_id,
            'surec': self.surec,
            'caller': self.caller,
            'state_ekleme_acikmi': state_ekleme_acikmi,
        }

class AksiyonEkleBlok(BaseBlok):
    def sablon_adini_getir(self):
        return 'stratejiler/parcalar/aksiyon_parcalar/aksiyon_ekle.html'

    def icerik_verilerini_getir(self):
        
        strateji = get_object_or_404(Strateji, id=self.strateji_id, kullanici=self.request.user)
        market_tipi = strateji.market_tipi
        aksiyon_gruplari = StratejiAksiyonu.AKSIYON_GRUPLARI

        if market_tipi == "futures":
            uygun_aksiyonlar = (
                aksiyon_gruplari['futures'] +
                aksiyon_gruplari['ortak'] +
                aksiyon_gruplari['yardimci']
            )
        else:
            uygun_aksiyonlar = (
                aksiyon_gruplari['spot'] +
                aksiyon_gruplari['ortak'] +
                aksiyon_gruplari['yardimci']
            )

        parite_interval_market = PariteIntervalMarket.objects.filter(
            onay=True,
            market_id=1 if market_tipi == "spot" else 2
        )

        return {
            'parite_interval_market': parite_interval_market,
            'uygun_aksiyonlar': uygun_aksiyonlar,
            'blok_id': self.blok_id,
            'parent_id': self.parent_id,
            'strateji_id': self.strateji_id,
            'surec': self.surec,
        }

class LoopBlok(BaseBlok):
    def sablon_adini_getir(self):
        return 'stratejiler/parcalar/loop/loop_partial.html'

    def icerik_verilerini_getir(self):
        strateji = get_object_or_404(Strateji, id=self.strateji_id, kullanici=self.request.user)
        market_tipi = strateji.market_tipi

        # Loop tipi seçenekleri (geliştirilebilir)
        loop_tipleri = [
            ('kademeli_alim', 'Kademeli Alım'),
            ('kademeli_satis', 'Kademeli Satış'),
            ('iz_suren_stop_loop', 'İz Süren Stop'),
            ('sartli_takip', 'Şartlı Takip'),
            ('fiyat_bekle_loop', 'Fiyat Bekle'),
            ('indikatore_gore_kademe', 'İndikatöre Bağlı Kademe'),
            ('bekle_ve_yeniden_dene', 'Bekle ve Yeniden Dene'),
            ('zamana_bagli_loop', 'Zamana Bağlı'),

        ]

        return {
            'blok_id': self.blok_id,
            'parent_id': self.parent_id,
            'strateji_id': self.strateji_id,
            'surec': self.surec,
            'loop_tipleri': loop_tipleri,
            'caller': self.caller
        }

@login_required
def loop_blok_ekle(request):
    blok = LoopBlok(request)
    return HttpResponse(blok.render())

def loop_adim_ekle(request):
    loop_tipi = request.POST.get("loop_tipi")
    dongu_miktari = request.POST.get("dongu_miktari")
    blok_id = request.POST.get("blok_id")
    parent_id = request.POST.get("parent_id")
    strateji_id = request.POST.get("strateji_id")
    surec = request.POST.get("surec")

    try:
        dongu_sayisi = int(request.POST.get("dongu_sayisi", 1)) if dongu_miktari == "n_kez" else 1
    except ValueError:
        return HttpResponse("Geçersiz döngü sayısı", status=400)

    blok_sablon = {
        "kademeli_alim":         "stratejiler/parcalar/loop/kademeli_alim.html",
        "kademeli_satis":        "stratejiler/parcalar/loop/kademeli_satis.html",
        "iz_suren_stop_loop":    "stratejiler/parcalar/loop/iz_suren_stop_loop.html",
        "sartli_takip":          "stratejiler/parcalar/loop/sartli_takip.html",
        "fiyat_bekle_loop":      "stratejiler/parcalar/loop/fiyat_bekle_loop.html",
        "indikatore_gore_kademe":"stratejiler/parcalar/loop/indikatore_gore_kademe.html",
        "bekle_ve_yeniden_dene": "stratejiler/parcalar/loop/bekle_ve_yeniden_dene.html",
        "zamana_bagli_loop":     "stratejiler/parcalar/loop/zamana_bagli_loop.html",
    }.get(loop_tipi)

    if not blok_sablon:
        return HttpResponse("Geçersiz loop tipi", status=400)

    # Her adım için ayrı ayrı render
    adimlar_html = ""
    if dongu_sayisi >10:
        dongu_sayisi=10
    for i in range(dongu_sayisi):
        adim_html = render_to_string(blok_sablon, {
            "blok_id": blok_id,
            "parent_id": parent_id,
            "strateji_id": strateji_id,
            "surec": surec,
            "adim_no": i + 1
        })
        adimlar_html += adim_html
    return HttpResponse(adimlar_html)




@login_required  # Kullanıcının giriş yapmış olmasını zorunlu kılar
def stratejiler_index(request):

    if request.method == "POST":
        form_tipi = request.POST.get("form_tipi")
        
        if form_tipi == "yeni_strateji":
            strateji_adi = request.POST.get("strateji-adi", "").strip()
            strateji_aciklama = request.POST.get("strateji-aciklama", "").strip()
            aktif_mi=False
            sisttem_aktif_mi=True
            borsa = request.POST.get("borsa", "").strip()
            market_tipi = request.POST.get("market_tipi", "").strip()
            
            kullanici=request.user
            
            toplam_strateji = Strateji.objects.filter(kullanici=kullanici).count()
            if toplam_strateji>=10:
                return JsonResponse({"success":False, "error":"Maksimum 10 strateji oluşturulabilir."}, status=400)
            
            if not strateji_adi:
                return JsonResponse({"success":False,"error":"Strateji adı boş bırakılamaz."},status=400)
            
            if Strateji.objects.filter(adi=strateji_adi,kullanici=kullanici).exists():
                return JsonResponse({"success":False,"error":"Bu isimde bir strateji zaten var."})
            
            yeni_strateji = Strateji.objects.create(
                adi=strateji_adi,
                aciklama=strateji_aciklama,
                kullanici=kullanici,
                aktif_mi=aktif_mi,  # Varsayılan olarak aktif geliyor
                sistem_aktif_mi=sisttem_aktif_mi,  # Varsayılan olarak sistem aktif geliyor
                borsa=borsa,
                market_tipi=market_tipi,  # 
                
            )
            
            print(strateji_adi)
            print(strateji_aciklama)
            print(borsa)
            print(market_tipi)
            
            # İşlem başarılıysa JSON yanıt dönüyoruz:
            return JsonResponse({"success": True, "message": "Strateji başarıyla oluşturuldu."})
        elif form_tipi == "ayrintilar":
            pass
    
    
    kullanici=request.user
    stratejiler=Strateji.objects.filter(kullanici=kullanici)
    al_kosullari=StratejiKosullari.objects.filter(strateji__kullanici=kullanici, islem_operator__op_sembol="BUY")
    sat_kosullari=StratejiKosullari.objects.filter(strateji__kullanici=kullanici, islem_operator__op_sembol="SELL")
    
    operatorler = Operatorler.objects.all()
    context={
        "operatorler": operatorler,
        "stratejiler": stratejiler,
        "al_kosullari": al_kosullari,
        "sat_kosullari": sat_kosullari}
    return render(request, "stratejiler/stratejiler_index.html", context)

@login_required
def strateji_detay(request, strateji_id):
    kullanici = request.user
    strateji = get_object_or_404(Strateji, id=strateji_id)

    # Kullanıcının sahip olduğu strateji koşullarını al
    al_kosullari = StratejiKosullari.objects.filter(strateji__kullanici=kullanici, islem_operator__op_sembol="BUY")
    sat_kosullari = StratejiKosullari.objects.filter(strateji__kullanici=kullanici, islem_operator__op_sembol="SELL")

    # AND ve OR bağlantılarını ekleyelim
    for kosul in al_kosullari:
        kosul.and_baglanti = kosul.baglantilar.filter(mantiksal_operator__op_sembol="AND").first()
        kosul.or_baglanti = kosul.baglantilar.filter(mantiksal_operator__op_sembol="OR").first()

    for kosul in sat_kosullari:
        kosul.and_baglanti = kosul.baglantilar.filter(mantiksal_operator__op_sembol="AND").first()
        kosul.or_baglanti = kosul.baglantilar.filter(mantiksal_operator__op_sembol="OR").first()

    # Mantıksal operatörleri çekelim (AND, OR, NOT gibi)
    operatorler = Operatorler.objects.filter(op_grubu="mantiksal")

    context = {
        "strateji": strateji,
        "al_kosullari": al_kosullari,
        "sat_kosullari": sat_kosullari,
        "operatorler": operatorler
    }
    return render(request, "stratejiler/strateji_detay.html", context)

@login_required
def strateji_icerigi_olustur(request, strateji_id):

    kullanici=request.user
    strateji = get_object_or_404(Strateji, id=strateji_id, kullanici=kullanici)
    kosullar=StratejiKosullari.objects.filter(strateji=strateji,)
    # Pariteler: spot veya futures
    if strateji.market_tipi == "spot":
        # Normal pariteler: spot market_id=1
        pariteler = PariteIntervalMarket.objects.filter(
            onay=True,
            market_id=1,
            parite__tip="parite"
        )
        # Endeksler: market null olabilir
        endeksler = PariteIntervalMarket.objects.filter(
            onay=True,
            parite__tip="endeks"
        )
    else:
        pariteler = PariteIntervalMarket.objects.filter(
            onay=True,
            market_id=2,
            parite__tip="parite"
        )
        endeksler = PariteIntervalMarket.objects.filter(
            onay=True,
            parite__tip="endeks"
        )

    # Sonuçları birleştir
    parite_interval_market = list(chain(pariteler, endeksler))

    indikatorler = Indikatorler.objects.filter(aktif_mi=True)
    operatorler = Operatorler.objects.all()

    indikator_listesi = []
    for indikator in indikatorler:
        # Parametre ve çıktı nesnelerini alın
        parametreler = list(IndikatorParametreleri.objects.filter(indikator=indikator))
        ciktilar = list(IndikatorCiktilari.objects.filter(indikator=indikator))



        indikator_listesi.append({
            'indikator': indikator,
            'parametreler': parametreler,
            'ciktilar': ciktilar,
        })

    context = {
        'strateji':strateji,
        'kosullar':kosullar,
        'operatorler':operatorler,
        'indikator_listesi': indikator_listesi,
        'parite_interval_market':parite_interval_market,
    }

    return render(request, 'stratejiler/strateji_icerigi_olustur.html', context)

def strateji_kosulu_kaydet(request):
    if request.method == "POST":
        try:
            data = request.POST  # JSON verisini al 
            print(f"data:{data}")

            for key, value in data.items():
                print(f"{key}: {value}")
                
            # 📌 1️⃣ Stratejiyi Al veya Oluştur
            strateji = get_object_or_404(Strateji, id=data.get("strateji_id"))


            # 📌 2️⃣ İşlem Operatörünü (BUY/SELL) Al
            islem_operator = get_object_or_404(Operatorler, op_sembol=data.get("yon"), op_grubu="islem")

            # 📌 3️⃣ Karşılaştırma Operatörünü (EQ, LT, GT, vb.) Al
            karsilastirma_operator = get_object_or_404(Operatorler, id=data.get("operator"), op_grubu="karsilastirma")

            # 📌 5️⃣ İlk ve Son İndikatörleri Kaydet
            ilk_indikator = get_object_or_404(Indikatorler, id=data.get("ilk_indikator"))
            ilk_indikator_ciktisi = get_object_or_404(IndikatorCiktilari, cikti_adi=data.get("secili_cikti_ilk"))

            son_indikator = get_object_or_404(Indikatorler, id=data.get("son_indikator"))
            son_indikator_ciktisi = get_object_or_404(IndikatorCiktilari, cikti_adi=data.get("secili_cikti_son"))


            # 📌 6️⃣ Parite-Interval-Market ID'lerini **Güvenli Şekilde Al**
            ilk_parite_interval_market_id = data.get("ilk_indikator_parite_interval_market[]")
            son_parite_interval_market_id = data.get("son_indikator_parite_interval_market[]")

            if not ilk_parite_interval_market_id or not son_parite_interval_market_id:
                raise ValueError("Parite Interval Market bilgisi eksik!")

            ilk_parite_interval_market = get_object_or_404(PariteIntervalMarket, id=int(ilk_parite_interval_market_id))
            son_parite_interval_market = get_object_or_404(PariteIntervalMarket, id=int(son_parite_interval_market_id))


            # 📌 4️⃣ Kullanıcının girdisine göre `ifade`yi oluştur
            secili_cikti_ilk = data.get("secili_cikti_ilk")  # Örn: "ema_{period}"
            secili_cikti_son = data.get("secili_cikti_son")  # Örn: "ema_{period}"


            # 📌 İlk indikatörün tüm parametrelerini al
            ilk_parametreler = {key.replace("ilk_parametreler[", "").replace("]", ""): value
                                for key, value in data.items() if key.startswith("ilk_parametreler[")}

            # 📌 Son indikatörün tüm parametrelerini al
            son_parametreler = {key.replace("son_parametreler[", "").replace("]", ""): value
                                for key, value in data.items() if key.startswith("son_parametreler[")}

            print(f"İlk Parametreler: {ilk_parametreler}")
            print(f"Son Parametreler: {son_parametreler}")

            # 📌 Kullanıcının seçtiği çıktı formatında `{}` içinde yer alan değişkenleri değiştireceğiz
            secili_cikti_ilk = data.get("secili_cikti_ilk", "")
            secili_cikti_son = data.get("secili_cikti_son", "")

            # 📌 Parametreleri çıktı formatına yerleştir
            secili_cikti_ilk = secili_cikti_ilk.format(**ilk_parametreler)
            secili_cikti_son = secili_cikti_son.format(**son_parametreler)


            with transaction.atomic():  # ✅ Tüm işlemleri tek bir atomik işlem içinde gerçekleştiriyoruz

                # 📌 4️⃣ Strateji Koşulunu Kaydet
                strateji_kosulu = StratejiKosullari.objects.create(
                    strateji=strateji,
                    ifade=f"{secili_cikti_ilk} {karsilastirma_operator.op_sembol} {secili_cikti_son}",
                    karsilastirma_operator=karsilastirma_operator,
                    islem_operator=islem_operator
                )
                

                # 📌 7️⃣ İlk ve Son İndikatörleri Kaydet (Parite-Interval-Market ile ilişkilendirildi!)
                ilk_kosul_indikator = StratejiKosulIndikator.objects.create(
                    strateji_kosulu=strateji_kosulu,
                    indikator=ilk_indikator,
                    indikator_ciktisi=ilk_indikator_ciktisi,
                    indikator_sirasi="ilk",
                    parite_interval_market=ilk_parite_interval_market
                )

                son_kosul_indikator = StratejiKosulIndikator.objects.create(
                    strateji_kosulu=strateji_kosulu,
                    indikator=son_indikator,
                    indikator_ciktisi=son_indikator_ciktisi,
                    indikator_sirasi="ikinci",
                    parite_interval_market=son_parite_interval_market
                )
                
                # 📌 6️⃣ Parametreleri Kaydet
                for key, value in data.items():
                    if key.startswith("ilk_parametreler["):
                        param_adi = key.split("[")[1].replace("]", "")
                        param = get_object_or_404(IndikatorParametreleri, parametre_adi=param_adi, indikator=ilk_indikator)
                        StratejiKosulParametreleri.objects.create(
                            kosul_indikator=ilk_kosul_indikator,
                            indikator_parametre=param,
                            kullanici_degeri=value
                        )

                    elif key.startswith("son_parametreler["):
                        param_adi = key.split("[")[1].replace("]", "")
                        param = get_object_or_404(IndikatorParametreleri, parametre_adi=param_adi, indikator=son_indikator)
                        StratejiKosulParametreleri.objects.create(
                            kosul_indikator=son_kosul_indikator,
                            indikator_parametre=param,
                            kullanici_degeri=value
                        )
                        
                # # 📌 7️⃣ Mantıksal Bağlantılar (AND/OR) Kaydet
                # if "or_grup_id" in data:
                #     mantiksal_operator = get_object_or_404(Operatorler, id=data.get("mantiksal_operator"), op_grubu="mantiksal")

                #     or_grup = StratejiKosulBaglantilari.objects.filter(
                #         kosullar__strateji=strateji, kosullar__sira=data.get("or_grup_id")
                #     ).first()

                #     if or_grup:
                #         or_grup.kosullar.add(strateji_kosulu)
                #     else:
                #         or_grup = StratejiKosulBaglantilari.objects.create(mantiksal_operator=mantiksal_operator)
                #         or_grup.kosullar.add(strateji_kosulu)     
                        
                        
                return JsonResponse({"status": "success", "message": "Veriler başarıyla kaydedildi!"})
        
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

def kosul_bagla(request):
    if request.method == "POST":
        try:
            kosul1_id = request.POST.get("kosul1")
            kosul2_id = request.POST.get("kosul2")
            operator_id = request.POST.get("operator")

            kosul1 = get_object_or_404(StratejiKosullari, id=kosul1_id)
            kosul2 = get_object_or_404(StratejiKosullari, id=kosul2_id)
            operator = get_object_or_404(Operatorler, id=operator_id)

            # Yeni bağlantıyı oluştur
            baglanti = StratejiKosulBaglantilari.objects.create(mantiksal_operator=operator)
            baglanti.kosullar.add(kosul1, kosul2)
            baglanti.save()

            return JsonResponse({"status": "success", "message": "Koşullar başarıyla bağlandı!"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Geçersiz istek!"}, status=400)

def strateji_sil(request, strateji_id):
    try:
        strateji = get_object_or_404(Strateji, id=strateji_id, kullanici=request.user)
        strateji.delete()
        return redirect('stratejiler:stratejiler_index')
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

@login_required
def kosul_sil(request):
    if request.method == "POST":
        kosul_id = request.POST.get("kosul_id")
        kosul = get_object_or_404(StratejiKosullari, id=kosul_id)

        # Kullanıcı kontrolü (Yetkisiz silme işlemlerini önler)
        if kosul.strateji.kullanici != request.user:
            return JsonResponse({"status": "error", "message": "Sizin böyle bir koşulunuz yok!"}, status=403)

        try:
            with transaction.atomic():  # ✅ Tüm işlemleri tek bir atomik işlem içinde gerçekleştiriyoruz
                
                # 📌 1️⃣ StratejiKoşulu'na bağlı tüm `StratejiKosulParametreleri` kayıtlarını sil
                StratejiKosulParametreleri.objects.filter(kosul_indikator__strateji_kosulu=kosul).delete()

                # 📌 2️⃣ StratejiKoşulu'na bağlı tüm `StratejiKosulIndikator` kayıtlarını sil
                StratejiKosulIndikator.objects.filter(strateji_kosulu=kosul).delete()

                # 📌 3️⃣ Son olarak StratejiKoşulu'nu sil
                kosul.delete()

            return JsonResponse({"status": "success", "message": "Koşul başarıyla silindi."})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Geçersiz istek."}, status=400)

def ilk_secim_ajax(request):
    if request.method == "POST":
        indikator_id = request.POST.get('indikator_id')
        try:
            indikator = Indikatorler.objects.get(id=indikator_id)
            # Parametreleri ve çıktıları alıyoruz
            ilk_secim_parametreler = IndikatorParametreleri.objects.filter(indikator=indikator)
            ilk_secim_ciktilar = IndikatorCiktilari.objects.filter(indikator=indikator)

            # Parametreleri JSON formatında hazırlıyoruz
            parametreler_data = [
                {'id': param.id, 'parametre_adi': param.parametre_adi,'varsayilan_deger':param.varsayilan_deger,'aciklama':param.aciklama,'indikator_adi':param.indikator_adi} for param in ilk_secim_parametreler]
            
            ciktilar_data = [
                {'id': cikti.id, 'cikti_adi': cikti.cikti_adi,'aciklama':cikti.cikti_adi,'indikator_adi':cikti.indikator_adi} for cikti in ilk_secim_ciktilar]

            # Response'u JSON olarak döndürüyoruz
            return JsonResponse({
                'success': True,
                'parametreler': parametreler_data,
                'ciktilar': ciktilar_data
            })
        except Indikatorler.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'İndikatör bulunamadı.'})

    return JsonResponse({'success': False, 'message': 'Geçersiz istek.'})
        
def son_secim_ajax(request):
    if request.method == "POST":
        indikator_id = request.POST.get('indikator_id')
        try:
            indikator = Indikatorler.objects.get(id=indikator_id)
            # Parametreleri ve çıktıları alıyoruz
            ilk_secim_parametreler = IndikatorParametreleri.objects.filter(indikator=indikator)
            ilk_secim_ciktilar = IndikatorCiktilari.objects.filter(indikator=indikator)

            # Parametreleri JSON formatında hazırlıyoruz
            parametreler_data = [
                {'id': param.id, 'parametre_adi': param.parametre_adi,'varsayilan_deger':param.varsayilan_deger,'aciklama':param.aciklama,'indikator_adi':param.indikator_adi} for param in ilk_secim_parametreler]
            
            ciktilar_data = [
                {'id': cikti.id, 'cikti_adi': cikti.cikti_adi,'aciklama':cikti.cikti_adi,'indikator_adi':cikti.indikator_adi} for cikti in ilk_secim_ciktilar]

            # Response'u JSON olarak döndürüyoruz
            return JsonResponse({
                'success': True,
                'parametreler': parametreler_data,
                'ciktilar': ciktilar_data
            })
        except Indikatorler.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'İndikatör bulunamadı.'})

    return JsonResponse({'success': False, 'message': 'Geçersiz istek.'})
        
def market_select(request):
    print("🔍 market_select VIEW çalıştı!")
    marketler = MarketType.objects.all()
    print("🎯 Gelen marketler:", list(marketler))
    return render(request, "stratejiler/parcalar/market_select.html", {
        "marketler": marketler
    })

@login_required
def yeni_kosul_formu(request):
    return render(request, "stratejiler/parcalar/yeni_kosul_formu.html")

@login_required
def strateji_editor(request):
    return render(request, "stratejiler/strateji_editor.html")

@login_required
def coin_kumesi_select(request):
    return HttpResponse("<p>Coin seçimi gelecektir.</p>")

@login_required
def karsilastirma_operatorleri_getir(request):
    blok_id = request.POST.get("blok_id")
    parent_id = request.POST.get("parent_id")
    
    operatorler=Operatorler.objects.filter(op_grubu="karsilastirma")
    return render(request, 'stratejiler/parcalar/karsilastirma_operatorleri.html',{
        'operatorler': operatorler,
        'blok_id': blok_id,
        'parent_id': parent_id
        })

@login_required
def indikator_parametre_partial(request):
    indikator_id = request.POST.get("indikator_id")
    blok_id = request.POST.get("blok_id")
    parent_id = request.POST.get("parent_id")
    konum = request.POST.get("konum")  # "sol" ya da "sag"
    
    if indikator_id in (None, "", "0"):  # boş seçimleri yakala
        return HttpResponse("")  # alanı temizle (hiçbir şey döndürme)
    try:
        indikator_id = int(indikator_id)
    except ValueError:
        return HttpResponse("Geçersiz ID", status=400)
    
    parametreler_queryset = IndikatorParametreleri.objects.filter(indikator_id=indikator_id)
    ciktilar_queryset = IndikatorCiktilari.objects.filter(indikator_id=indikator_id)

    # Dict olarak parametreleri hazırlayalım
    parametreler = [
        {
            "adi": p.parametre_adi,
            "default_deger": p.varsayilan_deger,
            "aciklama": p.aciklama or ""
        }
        for p in parametreler_queryset
    ]

    # Dict olarak çıktıları hazırlayalım
    ciktilar = [
        {
            "adi": c.cikti_adi,
            "aciklama": c.aciklama or ""
        }
        for c in ciktilar_queryset
    ]

    return render(request, "stratejiler/parcalar/indikator_parametre_inputlari.html", {
        "parametreler": parametreler,
        "ciktilar": ciktilar,
        "blok_id": blok_id,
        "parent_id": parent_id,
        "konum": konum
    })

@check_user_authenticated
def if_blogu_partial(request):
    blok = IfBlok(request)
    return HttpResponse(blok.render())

@login_required
def aksiyon_ekle(request):
    blok = AksiyonEkleBlok(request)
    return HttpResponse(blok.render())

def aksiyon_form(request):
    blok_id = request.POST.get("blok_id")
    parent_id = request.POST.get("parent_id")
    aksiyon_turu = request.POST.get("aksiyon_turu")
    strateji_id = request.POST.get("strateji_id")
    surec = request.POST.get("surec")
    
    print("POST ile gelen aksiyon_turu:", aksiyon_turu)
    print("POST ile gelen strateji_id:", strateji_id)
    market_tipi = None
    
    AKSIYON_TIPLERI_DICT = dict(StratejiAksiyonu.AKSIYON_TIPLERI)

    if not aksiyon_turu or aksiyon_turu not in AKSIYON_TIPLERI_DICT:
        return HttpResponse("Geçersiz aksiyon tipi", status=400)


    if strateji_id:
        try:
            strateji = Strateji.objects.get(id=strateji_id, kullanici=request.user)
            market_tipi = strateji.market_tipi
        except Strateji.DoesNotExist:
            pass
    
    print("Market tipi:", market_tipi)
    
    template_path = StratejiAksiyonu.AKSIYON_TEMPLATE_MAPPING.get(
        aksiyon_turu, 'aksiyon_parcalar/bos.html'
    )

    # Sadece ‘parite’ tipindekileri al
    pariteler_qs = Pariteler.objects.filter(onay=True, tip='parite')
    # Alternatif olarak: Pariteler.objects.filter(onay=True).exclude(tip='endeks')

    # Sadece parite isimlerini çek, tekrarları kaldır
    pariteler = list(
        pariteler_qs
        .values_list('pariteler', flat=True)
        .distinct()
    )

    if surec == "pre_buy":
        inside_buy_buton_izni = True
        after_sell_buton_izni = False
    elif surec == "inside_buy":
        inside_buy_buton_izni = False
        after_sell_buton_izni = True
    elif surec == "after_sell":
        inside_buy_buton_izni = False
        after_sell_buton_izni = False
    return render(request, f'stratejiler/parcalar/{template_path}', {
        'pariteler': pariteler,
        'market_tipi': market_tipi,

        'blok_id':blok_id,
        'parent_id':parent_id,
        'aksiyon_turu':aksiyon_turu,
        'strateji_id':strateji_id,
        'surec':surec,
        'after_sell_buton_izni': after_sell_buton_izni,
        'inside_buy_buton_izni': inside_buy_buton_izni,
    })

def inside_buy_ekle(request): 
    parent_id = request.POST.get('blok_id')
    strateji_id = request.POST.get('strateji_id')
    surec = request.POST.get('surec') 
    # yeni_blok_id = str(uuid.uuid4())
    yeni_blok_id = str(uuid.uuid4())[:4]
    

    if surec == "pre_buy":
        surec="inside_buy"
    elif surec == "inside_buy":
        surec="after_sell"
        
    context={
        'blok_id': yeni_blok_id,
        'parent_id': parent_id,
        'strateji_id':strateji_id,
        'surec':surec,
        
    }
    return render(request, "stratejiler/parcalar/sablonlar/inside_buy.html",context)

def after_sell_ekle(request): 
    parent_id = request.POST.get('blok_id')
    strateji_id = request.POST.get('strateji_id')
    surec = request.POST.get('surec') 
    # yeni_blok_id = str(uuid.uuid4())
    yeni_blok_id = str(uuid.uuid4())[:4]
    

    if surec == "pre_buy":
        surec="inside_buy"
    elif surec == "inside_buy":
        surec="after_sell"
        
    context={
        'blok_id': yeni_blok_id,
        'parent_id': parent_id,
        'strateji_id':strateji_id,
        'surec':surec,
        
    }
    return render(request, "stratejiler/parcalar/sablonlar/after_sell.html",context)

def data_save(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    gelen_veri = request.POST.dict()  # sadece düz veriler (tekli inputlar)
    
    # Eğer checkbox, multi-select varsa:
    # gelen_veri = {k: request.POST.getlist(k) for k in request.POST.keys()}

    pprint(gelen_veri)

    return JsonResponse({
        'status': 'success',
        'alınan_input_sayisi': len(gelen_veri),
        'veriler': gelen_veri,
    })

def ic_ve_grubu_ekle(request):
    parent_id = request.GET.get('blok_id')  # parent blok id
    print(f"parent_id:{parent_id}")
    strateji_id = request.GET.get('strateji_id')
    print(f"strateji_id:{strateji_id}")
    poz = request.GET.get('poz')
    
    surec = request.GET.get('surec')
    print(surec)
    print(f"surec:{surec}")
    if surec == "inside_buy":
        loop_btn_izni = True
    else:
        loop_btn_izni = False
    # yeni_blok_id = str(uuid.uuid4())
    yeni_blok_id = str(uuid.uuid4())[:4]
    context = {
        'blok_id': yeni_blok_id,
        'parent_id': parent_id,
        'strateji_id': strateji_id,
        'surec':surec,
        'poz':poz,
        'loop_btn_izni': loop_btn_izni
    }
    return render(request, "stratejiler/parcalar/sablonlar/ic_ve_sablonu.html", context)

# *
def veya_grubu_ekle(request):
    parent_id = request.GET.get('blok_id')  # parent blok id
    print(f"parent_id:{parent_id}")
    strateji_id = request.GET.get('strateji_id')
    surec = request.GET.get('surec')
    
    print(f"strateji_id:",strateji_id)
    # yeni_blok_id = str(uuid.uuid4())
    yeni_blok_id = str(uuid.uuid4())[:4]
    context = {
        'blok_id': yeni_blok_id,
        'parent_id': parent_id,
        'strateji_id': strateji_id,
        'surec':surec
    }
    return render(request, "stratejiler/parcalar/sablonlar/veya_sablonu.html", context)

def state_ekle(request):
    parent_id = request.GET.get('blok_id')  # parent blok id
    strateji_id = request.GET.get('strateji_id')
    surec = request.GET.get('surec')
    yeni_blok_id = str(uuid.uuid4())[:4]

    context = {
        'blok_id': yeni_blok_id,
        'parent_id': parent_id,
        'strateji_id': strateji_id,
        'surec':surec,
        'isaret_kapanma_sarti':0
    }
    return render(request, "stratejiler/parcalar/state/if_state.html", context)

def if_state_kapanma_sarti(request):
    strateji_id = request.GET.get('strateji_id')
    surec = request.GET.get('surec')
    strateji = get_object_or_404(Strateji, id=strateji_id, kullanici=request.user)
    market_tipi = strateji.market_tipi
    
    print(f"Market tipi: {market_tipi}")
    
    parent_id = request.GET.get("blok_id")  # ← burada aldık
    # yeni_blok_id = str(uuid.uuid4())
    yeni_blok_id = str(uuid.uuid4())[:4]
    
    # Pariteler: spot veya futures
    if strateji.market_tipi == "spot":
        # Normal pariteler: spot market_id=1
        pariteler = PariteIntervalMarket.objects.filter(
            onay=True,
            market_id=1,
            parite__tip="parite"
        )
        # Endeksler: market null olabilir
        endeksler = PariteIntervalMarket.objects.filter(
            onay=True,
            parite__tip="endeks"
        )
    else:
        pariteler = PariteIntervalMarket.objects.filter(
            onay=True,
            market_id=2,
            parite__tip="parite"
        )
        endeksler = PariteIntervalMarket.objects.filter(
            onay=True,
            parite__tip="endeks"
        )

    # Sonuçları birleştir
    parite_interval_market = list(chain(pariteler, endeksler))

    indikatorler = Indikatorler.objects.filter(aktif_mi=True)

    indikator_listesi = []
    for indikator in indikatorler:
        # Parametre ve çıktı nesnelerini alın
        parametreler = list(IndikatorParametreleri.objects.filter(indikator=indikator))
        ciktilar = list(IndikatorCiktilari.objects.filter(indikator=indikator))

        indikator_listesi.append({
            'indikator': indikator,
            'parametreler': parametreler,
            'ciktilar': ciktilar,
        })

    return render(request, 'stratejiler/parcalar/state/if_state_kapanma_sarti.html', {
        'parite_interval_market': parite_interval_market,
        'indikator_listesi': indikator_listesi,
        'blok_id': yeni_blok_id,     # Yeni blok bu
        'parent_id': parent_id,      # Eski blok (kapsayan)
        'strateji_id': strateji_id,
        'surec':surec
    })

def proses_ekle(request):
    blok_id = request.GET.get('blok_id')  # parent blok id
    strateji_id = request.GET.get('strateji_id')
    surec = request.GET.get('surec')
    request.GET.get("state_name")
    
    # yeni_blok_id = str(uuid.uuid4())
    yeni_blok_id = str(uuid.uuid4())[:4]
    
    context = {
        'blok_id': yeni_blok_id,
        'parent_id': blok_id,
        'strateji_id': strateji_id,
        'surec':surec
    }
    return render(request, "stratejiler/parcalar/proses/proses_blok.html", context)

def test_htmx_sayfasi(request):
    return render(request, 'stratejiler/test_htmx.html')






# binance'dan kaldıraç alama kodu:

