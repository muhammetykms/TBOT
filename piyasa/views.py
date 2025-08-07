from django.shortcuts import render
import pandas as pd
from .services import PiyasaServisi, TotalVeriServisi

def ozet_panel(request):
    
    total3=TotalVeriServisi.total3_kapanis_verilerini_al()
    print(total3)
    # exit()
    df = PiyasaServisi.binance_tum_coinleri_al()
    df = PiyasaServisi.filtrele_hacme_gore(df)

    # 🔧 HATALI OLAN BU: df.to_numeric(...) ❌
    df['quoteVolume'] = pd.to_numeric(df['quoteVolume'], errors='coerce')  # ✅ DOĞRU ŞEKİLDE

    print(df[['symbol', 'quoteVolume']].sort_values(by='quoteVolume', ascending=False).head(10))
    df['volatilite_yuzde'] = ((df['highPrice'] - df['lowPrice']) / df['openPrice']) * 100
    df['volatilite_yuzde'] = df['volatilite_yuzde'].round(2)
    df['symbol'] = df['symbol'].str.replace('USDT', '/USDT')

    ozet = PiyasaServisi.piyasa_ozeti(df)
    dominans = PiyasaServisi.btc_dominans()
    yorum = PiyasaServisi.otomatik_yorum(df)
    artanlar = PiyasaServisi.en_cok_artan(df)
    dusenler = PiyasaServisi.en_cok_dusen(df)
    volatil = PiyasaServisi.en_volatil(df)
    tum_coinler = df.sort_values(by='quoteVolume', ascending=False).copy()


    context = {
        "artan_sayi": ozet["artan_sayi"],
        "dusen_sayi": ozet["dusen_sayi"],
        "ortalama_volatilite": ozet["ortalama_volatilite"],
        "toplam_hacim": ozet["toplam_hacim"],
        "btc_dominans": dominans,
        "yorum": yorum,
        "artanlar": artanlar.to_dict('records'),
        "dusenler": dusenler.to_dict('records'),
        "volatil": volatil.to_dict('records'),
        "tum_coinler": df.sort_values(by='quoteVolume', ascending=False).to_dict('records'),
        "total3":total3
    }

    return render(request, "piyasa/ozet_panel.html", context)
