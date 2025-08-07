import requests
import pandas as pd
import ta
from datetime import datetime

class PiyasaServisi:

    @staticmethod
    def binance_tum_coinleri_al():
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url)
        df = pd.DataFrame(response.json())

        # 🔍 Sadece USDT paritesindekiler alınsın
        df = df[df['symbol'].str.endswith('USDT')]

        # ✅ Sayısal dönüşümleri tek tek kolonlara uygula
        kolonlar = ['priceChangePercent', 'highPrice', 'lowPrice', 'openPrice', 'quoteVolume']
        for kolon in kolonlar:
            df[kolon] = pd.to_numeric(df[kolon], errors='coerce')

        return df



    @staticmethod
    def coin_dagilimi(df):
        artan_1 = df[(df['priceChangePercent'] > 0) & (df['priceChangePercent'] <= 1)].shape[0]
        artan_5 = df[(df['priceChangePercent'] > 1) & (df['priceChangePercent'] <= 5)].shape[0]
        artan_5up = df[df['priceChangePercent'] > 5].shape[0]
        dusen_1 = df[(df['priceChangePercent'] < 0) & (df['priceChangePercent'] >= -1)].shape[0]
        dusen_5 = df[(df['priceChangePercent'] < -1) & (df['priceChangePercent'] >= -5)].shape[0]
        dusen_5down = df[df['priceChangePercent'] < -5].shape[0]
        return {
            "artan_0_1": artan_1,
            "artan_1_5": artan_5,
            "artan_5+": artan_5up,
            "dusen_0_1": dusen_1,
            "dusen_1_5": dusen_5,
            "dusen_5-": dusen_5down
        }

    @staticmethod
    def piyasa_ozeti(df):
        artan = df[df['priceChangePercent'] > 0]
        dusen = df[df['priceChangePercent'] < 0]
        ort_vol = ((df['highPrice'] - df['lowPrice']) / df['openPrice']).mean() * 100
        toplam_hacim = df['quoteVolume'].sum()
        return {
            "artan_sayi": len(artan),
            "dusen_sayi": len(dusen),
            "ortalama_volatilite": round(ort_vol, 2),
            "toplam_hacim": round(toplam_hacim, 2)
        }

    @staticmethod
    def en_cok_artan(df, n=5):
        return df.sort_values(by='priceChangePercent', ascending=False).head(n)

    @staticmethod
    def en_cok_dusen(df, n=5):
        return df.sort_values(by='priceChangePercent').head(n)

    @staticmethod
    def en_volatil(df, n=5):
        df['volatilite_yuzde'] = ((df['highPrice'] - df['lowPrice']) / df['openPrice']) * 100
        return df.sort_values(by='volatilite_yuzde', ascending=False).head(n)

    @staticmethod
    def btc_dominans():
        url = "https://api.coingecko.com/api/v3/global"
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()  # HTTP hatalarını fırlatır
            json_data = r.json()

            if "data" in json_data and "market_cap_percentage" in json_data["data"]:
                return round(json_data["data"]["market_cap_percentage"]["btc"], 2)
            else:
                print("⚠️ CoinGecko yanıtında beklenen 'data' alanı yok.")
                return None

        except Exception as e:
            print(f"CoinGecko BTC dominans hatası: {e}")
            return None



    @staticmethod
    def otomatik_yorum(df):
        oz = PiyasaServisi.piyasa_ozeti(df)
        btc_df = df[df['symbol'] == 'BTCUSDT']
        btc_change = btc_df.iloc[0]['priceChangePercent'] if not btc_df.empty else 0
        yorum = "Bugün piyasa "
        if oz['artan_sayi'] > oz['dusen_sayi']:
            yorum += "genel olarak pozitif seyrediyor. "
        elif oz['artan_sayi'] < oz['dusen_sayi']:
            yorum += "negatif ağırlıklı bir gün yaşanıyor. "
        else:
            yorum += "durağan bir yapı gösteriyor. "

        yorum += f"Ortalama volatilite %{oz['ortalama_volatilite']} civarında. "
        yorum += f"BTC son 24 saatte %{round(btc_change, 2)} hareket etti."
        return yorum

    @staticmethod
    def filtrele_hacme_gore(df, min_hacim=160_000_000):
        # Sadece USDT paritesindeki coinleri alalım
        df = df[df['symbol'].str.endswith('USDT')]
        # Ardından hacim filtresi uygula
        return df[df['quoteVolume'] > min_hacim]




class TotalVeriServisi:

    @staticmethod
    def total3_kapanis_verilerini_al(days=90):
        import requests
        import pandas as pd
        import ta
        from datetime import datetime

        # 1. BTC ve ETH verilerini çek
        btc_url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}"
        eth_url = f"https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days={days}"

        btc_response = requests.get(btc_url)
        eth_response = requests.get(eth_url)

        if btc_response.status_code != 200 or eth_response.status_code != 200:
            raise Exception("BTC veya ETH verisi alınamadı.")

        btc_df = pd.DataFrame(btc_response.json()['market_caps'], columns=['timestamp', 'btc'])
        eth_df = pd.DataFrame(eth_response.json()['market_caps'], columns=['timestamp', 'eth'])

        # Timestamp'leri datetime'a çevir
        btc_df['date'] = pd.to_datetime(btc_df['timestamp'], unit='ms').dt.date
        eth_df['date'] = pd.to_datetime(eth_df['timestamp'], unit='ms').dt.date

        # Timestamp üzerinden merge
        df = pd.merge(btc_df[['date', 'btc']], eth_df[['date', 'eth']], on='date', how='inner')

        # 2. Anlık TOTAL market cap (global)
        global_url = "https://api.coingecko.com/api/v3/global"
        total_response = requests.get(global_url)
        if total_response.status_code != 200:
            raise Exception("Global verisi alınamadı.")

        total_market_cap = total_response.json()['data']['total_market_cap']['usd']
        df['total'] = total_market_cap
        df['total3'] = df['total'] - df['btc'] - df['eth']

        # 3. EMA hesapla
        df['EMA10'] = ta.trend.ema_indicator(df['total3'], window=10)
        df['EMA20'] = ta.trend.ema_indicator(df['total3'], window=20)
        df['EMA30'] = ta.trend.ema_indicator(df['total3'], window=30)
        df['EMA40'] = ta.trend.ema_indicator(df['total3'], window=40)
        df['EMA50'] = ta.trend.ema_indicator(df['total3'], window=50)

        son = df.dropna().iloc[-1]
        pozitif = (
            son['EMA10'] > son['EMA20'] > son['EMA30'] > son['EMA40'] > son['EMA50']
        )

        return {
            "pozitif_yapi": pozitif,
            "son_kapanis": round(son['total3'], 2),
            "tarih": str(son['date'])
        }
