from django.shortcuts import render, get_object_or_404
from .models import Pariteler, Interval, MarketType, PariteIntervalMarket
from pprint import pprint
from django.http import JsonResponse
import requests
# Create your views here.

def mumlar_index(request):
    
    
    context={}
    return render(request, "mumlar/mumlar_index.html",context)

def mum_verisi_getir(request):
    
    if request.method =="POST":
        pass
    
    
    context={}
    return render(request,"mumlar/mum_verilerini_incele",context)


def pariteler_ve_interval(request): # PArite-interval-MarketType 
    
    #   Güncelleme POSTU
    if request.method == "POST":
        # AJAX ile gelen verileri alın
        pariteintervalmarket_id = request.POST.get("id")
        new_status = request.POST.get("onay") == "true"  # Boolean'a çevir

        # PariteIntervalMarket kaydını güncelle
        pariteintervalmarket = get_object_or_404(PariteIntervalMarket, id=pariteintervalmarket_id)
        pariteintervalmarket.onay = new_status
        pariteintervalmarket.save()

        # Güncelleme sonrası döneceğimiz cevap
        return JsonResponse({"success": True, "onay": pariteintervalmarket.onay})

    # Tüm PariteIntervalMarket kayıtlarını alın
    pariteintervalmarkets = PariteIntervalMarket.objects.select_related('parite', 'interval', 'market').all()

    # İsteğe bağlı olarak filtreleme
    onay_filter = request.GET.get('onay', None)
    if onay_filter is not None:
        pariteintervalmarkets = pariteintervalmarkets.filter(onay=(onay_filter.lower() == 'true'))

    context = {'pariteintervalmarkets': pariteintervalmarkets}

    return render(request, "mumlar/pariteler_ve_interval.html", context)


def parite_ekle(request):
    if request.method == "POST":
        parite_adi = request.POST.get("parite_name")

        if parite_adi:
            parite_adi = parite_adi.upper()

            # Minimum uzunluk ve format kontrolü
            if len(parite_adi) < 6:  # Minimum uzunluk 4+2
                return JsonResponse({'success': False, 'error': 'Parite adı en az 6 karakter olmalı (örneğin: BTCUSDT).'})

            # Paritenin son kısmını kontrol et (örneğin: USDT veya USDC gibi)
            base_currency = parite_adi[-4:]  # Son 4 karakter
            if not base_currency.isalpha() or len(base_currency) < 4:
                return JsonResponse({'success': False, 'error': 'Parite adı geçerli bir baz para birimi içermeli (örneğin: USDT).'})

            # Benzersizlik kontrolü
            if Pariteler.objects.filter(pariteler=parite_adi).exists():
                return JsonResponse({'success': False, 'error': f"{parite_adi} zaten mevcut."})

            # Pariteyi kaydet
            parite = Pariteler.objects.create(pariteler=parite_adi)

            # Tüm Interval ve MarketType kombinasyonlarını oluştur
            intervals = Interval.objects.all()
            markets = MarketType.objects.all()

            for interval in intervals:
                for market in markets:
                    PariteIntervalMarket.objects.get_or_create(parite=parite, interval=interval, market=market)

            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'error': 'Parite adı boş olamaz.'})

    pariteler = Pariteler.objects.all()
    context = {"pariteler": pariteler}
    return render(request, "mumlar/parite_ekle.html", context)




# Futures tablosu varmı yokmu kontrolü bununla yapılır.
def is_symbol_available(symbol):
    base_url = "https://fapi.binance.com"
    endpoint = "/fapi/v1/exchangeInfo"

    # Binance Futures Exchange Info'yu al
    response = requests.get(base_url + endpoint)
    data = response.json()
    # pprint(data)
    # Symbol listesi kontrolü
    for item in data['symbols']:
        if item['symbol'] == symbol.upper():
            return True
    return False

    # # Örnek Kullanım
    # symbol = "ADAUSDT"
    # result = is_symbol_available(symbol)  # ".P" ekleyerek kontrol ediyoruz
    # print(f"{symbol}.P mevcut mu?: {result}")


