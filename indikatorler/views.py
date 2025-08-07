import pprint
import json
import requests
import datetime


#SAR için
import pandas as pd
import pandas_ta as ta
import numpy as np
import matplotlib.pyplot as plt


import ccxt


import matplotlib.pyplot as plt
import io
import urllib
import base64


# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

from .models import Indikatorler, IndikatorParametreleri, IndikatorCiktilari
from .services import IndikatorMotoru
from destek.services import *

from django.shortcuts import get_object_or_404, redirect, render
from .models import Indikatorler, IndikatorParametreleri, IndikatorCiktilari


def indikatorler_index(request):
        #   Güncelleme POSTU
    if request.method == "POST":
        # AJAX ile gelen verileri alın
        indikator_id = request.POST.get("id")
        new_status = request.POST.get("onay") == "true"  # Boolean'a çevir

        # indikator_verisi kaydını güncelle
        indikator_verisi = get_object_or_404(Indikatorler, id=indikator_id)
        indikator_verisi.aktif_mi = new_status
        indikator_verisi.save()

        # Güncelleme sonrası döneceğimiz cevap
        return JsonResponse({"success": True, "onay": indikator_verisi.aktif_mi})
    
    
    indikatorler=Indikatorler.objects.all()
    context={"indikatorler":indikatorler}
    return render(request, "indikatorler/indikatorler_index.html", context)


# Örnek veri oluştur
def get_sample_data():
    """ Aralıklı Mumları Getir """
    parite="AVAXUSDT"
    start_time_str="09-11-2018 00:00"
    end_time_str="12-12-2024 20:00"
    interval="4h"
    limit=None
    # Binance API base URL
    base_url = "https://api.binance.com"
    
    # Endpoint for klines
    endpoint = "/api/v3/klines"
    
    # Convert start_time_str to datetime object
    start_time = datetime.datetime.strptime(start_time_str, "%d-%m-%Y %H:%M")
    end_time = datetime.datetime.strptime(end_time_str, "%d-%m-%Y %H:%M")
    # Start time needs to be converted to milliseconds since epoch
    start_time_in_ms = int(start_time.timestamp() * 1000)
    
    end_time_in_ms=int(end_time.timestamp() * 1000)
    all_data = []
    max_limit = 1000  # Max limit per request set by Binance API
    
    while True:
        # Parameters for the API request
        params = {
            "symbol": parite,
            "interval": interval,
            "startTime": start_time_in_ms,
            "endTime":end_time_in_ms
        }
        
        # Making the API request
        response = requests.get(base_url + endpoint, params=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            
            if not data:
                print("veri yok.")
                break
            
            all_data.extend(data)
            
            if limit is not None:
                limit -= len(data)
                if limit <= 0:
                    break
            
            # Update start_time_in_ms to the timestamp of the last fetched kline
            start_time_in_ms = data[-1][0] + 1  # Increment to avoid overlapping
            
            if len(data) < max_limit:
                break  # If less than max limit is returned, end of data is reached
            
        else:
            print("Failed to fetch data:", response.status_code, response.text)
            return None
    
    df=binance_mum_to_df(all_data)
    return df


# View fonksiyonu
def indikatör_gorunum(request):
    # df = get_sample_data()
    # df = obv_ta(df)
    # df = vwap_haof_ta(df)
    # df = chaikin_money_flow_ta(df)
    # df = rsi_ta(df)
    # df = cmo_ta(df)
    # context = {
    #     'data': df.to_dict(orient='records')  # DataFrame'i sözlük listesine çeviriyoruz
    # }
    # return render(request, 'indikatorler/ind.html', context)
    pass


# Binance API'den veri çekme
def grafik_gorunum(request):
    # Veri çekme
    df = get_sample_data()
    
    if df is None or df.empty:
        return render(request, 'indikatorler/grafik.html', {'error': 'Veri bulunamadı.'})

    # Grafik oluşturma
    plt.figure(figsize=(10, 6))
    plt.plot(df['timestamp'], df['close'], marker='o', linestyle='-', color='blue')
    plt.title('Binance Mum Verileri')
    plt.xlabel('Tarih')
    plt.ylabel('Kapanış Fiyatı')
    plt.xticks(rotation=45)
    plt.grid(True)

    # Grafiği bir bellek dosyasına kaydetme
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Grafiği base64 formatına çevirme
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png).decode('utf-8')

    # Template'e gönderilecek context
    context = {
        'graphic': graphic
    }
    return render(request, 'indikatorler/grafik.html', context)


def calculate_indicator(request, indikator_adi):
    try:
        # Modelden indikatör bilgilerini al
        indikator = Indikatorler.objects.get(adi=indikator_adi)
        
        # Örnek veri
        veriler = {
            "close": [100, 105, 102, 108],
            "volume": [1000, 1200, 1100, 1300]
        }

        # İndikatör hesabı
        sonuc = IndikatorMotoru.hesapla(indikator, veriler)
        return JsonResponse({"success": True, "result": sonuc})
    
    except Indikatorler.DoesNotExist:
        return JsonResponse({"success": False, "error": "İndikatör bulunamadı"})
    except ValueError as e:
        return JsonResponse({"success": False, "error": str(e)})


def indikator_guncelle(request, id):
    # İndikatör bilgilerini al
    indikator = get_object_or_404(Indikatorler, id=id)

    if request.method == "POST":
        # print(request.POST)  # Gelen POST verilerini kontrol et

        # İndikatör bilgilerini güncelle
        indikator.adi = request.POST.get("indikator-adi", "")
        indikator.kutuphane = request.POST.get("kutuphane", "")
        indikator.aciklama = request.POST.get("indikator-aciklama", "")
        indikator.kullanim_aciklamasi = request.POST.get("kullanim-aciklamasi", "")
        indikator.indikator_ciftleri = request.POST.get("indikator_ciftleri", "")
        indikator.indikator_grubu = request.POST.get("indikator-grubu", "")
        indikator.save()

        indikator_adi=request.POST.get("indikator-adi", "")
        for key, value in request.POST.items():
            if key.startswith("parametreler") and "parametre_adi" in key:
                # Key'den 'id' bilgisi ayıklanıyor
                field_name, id_info = key.rsplit("-id", 1) if "-id" in key else (key, "new")

                parametre_adi = value
                varsayilan_deger = request.POST.get(
                    field_name.replace('parametre_adi', 'varsayilan_deger'), ""
                )
                
                print("varsayilan_deger",varsayilan_deger)

                if id_info == "new":  # Yeni kayıt oluşturuluyor
                    aciklama = request.POST.get(
                        field_name.replace('parametre_adi', 'aciklama'), ""
                    )
                    print("aciklama",aciklama)
                    IndikatorParametreleri.objects.create(
                        indikator_adi=indikator_adi,
                        indikator=indikator,
                        parametre_adi=parametre_adi,
                        varsayilan_deger=float(varsayilan_deger.replace(",", ".")) if varsayilan_deger else 0.0,
                        aciklama=aciklama
                    )
                else:  # Mevcut kayıt güncelleniyor
                    try:
                        aciklama = request.POST.get(
                            field_name.replace('parametre_adi', 'aciklama'), ""
                        )
                        print("aciklama",aciklama)
                        parametre = IndikatorParametreleri.objects.get(id=id_info)
                        parametre.parametre_adi = parametre_adi
                        parametre.varsayilan_deger = float(varsayilan_deger.replace(",", ".")) if varsayilan_deger else 0.0
                        parametre.aciklama = aciklama
                        parametre.indikator_adi=indikator_adi
                        parametre.save()
                    except IndikatorParametreleri.DoesNotExist:
                        pass  # İlgili ID bulunamazsa herhangi bir işlem yapma


        # Çıktıları işle
        for key, value in request.POST.items():
            if key.startswith("cikti") and "cikti_adi" in key:
                # Key'den 'id' bilgisi ayıklanıyor
                field_name, id_info = key.rsplit("-id", 1) if "-id" in key else (key, "new")

                cikti_adi = value  # Çıktı adı
                aciklama = request.POST.get(
                    field_name.replace('cikti_adi', 'aciklama'), ""
                )

                if id_info == "new":  # Yeni kayıt oluşturuluyor
                    IndikatorCiktilari.objects.create(
                        indikator_adi=indikator_adi,
                        indikator=indikator,
                        cikti_adi=cikti_adi,
                        aciklama=aciklama
                    )
                else:  # Mevcut kayıt güncelleniyor
                    try:
                        cikti = IndikatorCiktilari.objects.get(id=id_info)
                        cikti.indikator_adi=indikator_adi
                        cikti.cikti_adi = cikti_adi
                        cikti.aciklama = aciklama
                        cikti.save()
                    except IndikatorCiktilari.DoesNotExist:
                        pass  # İlgili ID bulunamazsa herhangi bir işlem yapma

        return redirect('indikatorler:indikatorler_index')

    # Context için mevcut parametreler ve çıktılar
    parametreler = IndikatorParametreleri.objects.filter(indikator=indikator)
    ciktilar = IndikatorCiktilari.objects.filter(indikator=indikator)
    context = {
        "indikator": indikator,
        "parametreler": parametreler,
        "ciktilar": ciktilar,
    }
    return render(request, 'indikatorler/indikator_guncelle.html', context)
