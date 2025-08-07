from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json
import threading
import requests
import time



import pprint

import talib
import pandas as pd
import requests

from binance.client import Client
from account.models import BinanceAPI

# client = Client(api_key, api_secret)

# Güncel fiyat bilgisi
# price = client.get_symbol_ticker(symbol="BNBUSDT")
# print(price)



def coin_adet_siniri():
    pass

def market_al(parite,adet):
    api_key, secret_key=db.client_getir()
    client=Client(api_key,secret_key)
    # Market alım emri
    order = client.order_market_buy(
        symbol=parite,
        quantity=adet  # Almak istediğiniz miktar
    )
    
    #   Emri kontrol etme.
    order_id = order["orderId"]
    order_status = client.get_order(symbol="BNBUSDT", orderId=order_id)
    print(order_status)
    

def market_sat(parite,adet):
    # Market satış emri
    api_key, secret_key=db.client_getir()
    client=Client(api_key,secret_key)
    
    order = client.order_market_sell(
        symbol="BNBUSDT",
        quantity=1  # Satmak istediğiniz miktar
    )
    #   Emri kontrol etme.
    order_id = order["orderId"]
    order_status = client.get_order(symbol="BNBUSDT", orderId=order_id)
    print(order_status)


def limit_al(parite,adet,alis_fiyati):
    # Limit alım emri (Örneğin: BNB 200 USDT olduğunda almak için)
    api_key, secret_key=db.client_getir()
    client=Client(api_key,secret_key)
    
    limit_buy_order = client.order_limit_buy(
        symbol=parite,
        quantity=adet,           # Almak istediğiniz miktar
        price=alis_fiyati        # İstediğiniz alış fiyatı
    )
    print(limit_buy_order)
    
    #   Gönderilen limit emirlerin durumunu kontrol etmek için get_order metodunu kullanabilirsiniz
    order_id = limit_buy_order["orderId"]
    order_status = client.get_order(symbol=parite, orderId=order_id)
    print(order_status)
    
    # "NEW": Emir yeni oluşturulmuş, henüz gerçekleştirilmemiş.
    # "PARTIALLY_FILLED": Emir kısmen gerçekleşmiş.
    # "FILLED": Emir tamamen gerçekleşmiş.
    # "CANCELED": Emir iptal edilmiş.
    # "REJECTED": Emir reddedilmiş.
    # "EXPIRED": Emir süresi dolmuş veya başka bir nedenle geçersiz hale gelmiş.


def limit_sat(parite,adet,satis_fiyati):
    # Limit satış emri (Örneğin: BNB 250 USDT olduğunda satmak için)
    
    api_key, secret_key=db.client_getir()
    client=Client(api_key,secret_key)
        
    limit_sell_order = client.order_limit_sell(
        symbol=parite,
        quantity=adet,           # Satmak istediğiniz miktar
        price=satis_fiyati        # İstediğiniz satış fiyatı
    )
    print(limit_sell_order)

    #   Gönderilen limit emirlerin durumunu kontrol etmek için get_order metodunu kullanabilirsiniz
    order_id = limit_sell_order["orderId"]
    order_status = client.get_order(symbol=parite, orderId=order_id)
    print(order_status)
    
    # "NEW": Emir yeni oluşturulmuş, henüz gerçekleştirilmemiş.
    # "PARTIALLY_FILLED": Emir kısmen gerçekleşmiş.
    # "FILLED": Emir tamamen gerçekleşmiş.
    # "CANCELED": Emir iptal edilmiş.
    # "REJECTED": Emir reddedilmiş.
    # "EXPIRED": Emir süresi dolmuş veya başka bir nedenle geçersiz hale gelmiş.


def acik_limit_emirler(parite):
    #   AÇık Limit Emirlerini Kontorl etme
    api_key, secret_key=db.client_getir()
    client=Client(api_key,secret_key)
    
    open_orders = client.get_open_orders(symbol=parite)
    print(open_orders)

def acik_emri_iptal_et(parite,order_id):
    #   Belirli Bir emiri iptal etme.
    api_key, secret_key=db.client_getir()
    client=Client(api_key,secret_key)
    
    cancel_order = client.cancel_order(symbol=parite, orderId=order_id)
    print(cancel_order)



""" MARJİN İŞLEMLER """



def izole_marjin_market_al(pair, yon ,sermaye, kaldirac):
    """
    İzole marjin hesabında kaldıraçlı market alım işlemi yapar.

    :param pair: İşlem çifti, örneğin 'BTCUSDT'
    :param yon: "BUY" ya da "SELL"
    :param sermaye: Kullanılacak sermaye miktarı (örneğin 100 USDT)
    :param kaldirac: Kullanılmak istenen kaldıraç oranı (örneğin 3, 5, 10)

    """
    
    try:
        # Kaldıraçlı işlem büyüklüğünü hesapla
        islem_miktari = sermaye * kaldirac
        api_key, secret_key=db.client_getir()
        client=Client(api_key,secret_key)
        # Mevcut fiyatı al
        fiyat = float(client.get_symbol_ticker(symbol=pair)['price'])
        
        # Alınacak miktarı hesapla
        miktar = islem_miktari / fiyat

        # İzole marjin market alım emri oluştur
        order = client.create_margin_order(
            symbol=pair,
            side=yon,
            type='MARKET',
            quantity=round(miktar, 6),  # Miktarı yuvarla (örneğin BTC için 6 ondalık basamak)
            isIsolated='TRUE'
        )

        print(f"{pair} çiftinde {kaldirac}x kaldıraç ile {round(miktar, 6)} birim alım yapıldı.")
        print("Alım emri detayı:", order)
        return order

    except Exception as e:
        print("Hata oluştu:", e)

# Örnek kullanım
# BTCUSDT işlem çiftinde 100 USDT ile 3x kaldıraçlı izole marjin alım işlemi yapma
# izole_marjin_market_al('BTCUSDT', sermaye=100, kaldirac=3)


def izole_marjin_cuzdanini_sorgula():
    """
    İzole marjin cüzdanındaki bakiyeleri ve borç bilgilerini sorgular.
    """
    try:
        api_key, secret_key=db.client_getir()
        client=Client(api_key,secret_key)
        response = client.get_isolated_margin_account()
        assets = response['assets']

        for asset in assets:
            symbol = asset['symbol']
            base_asset = asset['baseAsset']
            quote_asset = asset['quoteAsset']

            print(f"\nİşlem Çifti: {symbol}")
            print(f"    Ana Varlık ({base_asset['asset']}):")
            print(f"    Toplam Borç: {base_asset['borrowed']}")
            print(f"    Toplam Teminat: {base_asset['free']}")
            print(f"    Faiz: {base_asset['interest']}")
            
            print(f"  Karşıt Varlık ({quote_asset['asset']}):")
            print(f"    Toplam Borç: {quote_asset['borrowed']}")
            print(f"    Toplam Teminat: {quote_asset['free']}")
            print(f"    Faiz: {quote_asset['interest']}")

    except Exception as e:
        print("İzole marjin cüzdanı sorgulama hatası:", e)

# Örnek kullanım
# izole_marjin_cuzdanini_sorgula()



def marjin_varlik_detaylarini_sorgula(asset):
    """
    Belirli bir varlık için Binance marjin varlık detaylarını sorgular.
    """
    try:
        # Veritabanından API anahtarlarını çekme
        api_key, secret_key = db.client_getir()
        # Binance istemcisini oluşturma
        client = Client(api_key, secret_key)
        
        if not api_key or not secret_key:
            print("API Key veya Secret Key alınamadı.")
            return

        # Belirli bir varlık için marjin detaylarını sorgulama
        asset_details = client.get_margin_asset(asset=asset)
        
        # Tam yanıtı yazdırarak kontrol edelim
        print("Tam Yanıt:", asset_details)

        # Faiz oranını ve borç alınabilirliğini yazdırma
        daily_interest = asset_details.get('dailyInterest')
        borrowable = asset_details.get('borrowable')
        print(f"{asset}: Günlük Faiz Oranı: {daily_interest}, Borç Alınabilir: {borrowable}")

    except Exception as e:
        print("Marjin varlık detaylarını sorgulama hatası:", e)

# Örnek kullanım
# marjin_varlik_detaylarini_sorgula('BTC')








