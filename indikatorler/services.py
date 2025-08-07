from ta import momentum, trend

import pprint
import json
import requests
import datetime

#SAR için
import pandas as pd
import pandas_ta as ta
import numpy as np

from ta.trend import *
from ta.momentum import *
from ta.volatility import *
from ta.volume import *

from ta.others import *
from ta.utils import *
import ccxt


import matplotlib.pyplot as plt
import io
import urllib
import base64


# Create your views here.
from django.shortcuts import render

# from custom_indicators import custom_rsi  # Kendi algoritmanız

class IndikatorMotoru:
    """     TA KÜTÜPHANESİNİN İÇİNDEKİ GÖSTERGELER     """
    #   -----------     MOMENTUM - GÜÇ    -------------
        
    def rsi_ta(df, period=14):
        """
        RSI ve RSI ortalaması hesaplar.
        
        Args:
            df (DataFrame): Mum verileri.
            period (int): RSI hesaplama süresi.
            ortalama_tipi (str): 'sma' veya 'ema'
            ortalama_period (int or None): Ortalama hesaplama periyodu. None ise RSI periodu kullanılır.

        Returns:
            df (DataFrame): Yeni RSI sütunları eklenmiş DataFrame.
        """
        isim_rsi = f"rsi_{period}"
        isim_ortalama = f"rsi_ortalama_{period}"

        rsi = RSIIndicator(close=df['close'], window=period)
        df[isim_rsi] = rsi.rsi()

        ortalama_tipi = 'sma'  # ilerde çoktan seçmeli geliştirme yapılacak.
        if ortalama_tipi == 'sma':
            df[isim_ortalama] = df[isim_rsi].rolling(period).mean()
        elif ortalama_tipi == 'ema':
            df[isim_ortalama] = df[isim_rsi].ewm(span=period, adjust=False).mean()
        else:
            raise ValueError("ortalama_tipi 'sma' veya 'ema' olmalı")

        return df
    
    def cmo_ta(df, period=14):

        isim_cmo = f'cmo_{period}'
        src = df['close']

        # Chande Momentum Oscillator hesaplaması
        momm = src.diff()  # Kapanış fiyatlarındaki değişim

        # f1 ve f2 fonksiyonları
        def f1(m):
            return m if m >= 0 else 0

        def f2(m):
            return -m if m < 0 else 0

        # f1 ve f2 fonksiyonlarını uygulama
        m1 = momm.apply(f1)
        m2 = momm.apply(f2)

        # sm1 ve sm2'yi hesaplama
        sm1 = m1.rolling(window=period).sum()
        sm2 = m2.rolling(window=period).sum()

        # Chande Momentum Oscillator (CMO) hesaplama
        chandeMO = 100 * (sm1 - sm2) / (sm1 + sm2)

        # Sonuçları yazdırma
        df[isim_cmo] = chandeMO

        """
        Chande Momentum Oscillator (CMO) hesaplar.
        
        Parameters:
        - df: DataFrame, kapanış fiyatlarını içeren veri.
        - window: int, CMO hesaplamak için kullanılacak pencere süresi (varsayılan 14).

        Returns:
        - DataFrame: CMO değerini içeren yeni bir DataFrame.
        
        0 Seviyesi: CMO'nun sıfır değeri, pozitif ve negatif fiyat hareketlerinin birbirini dengelediği anlamına gelir. CMO sıfırın üzerinde olduğunda, yukarı yönlü momentum daha baskındır; sıfırın altında olduğunda, aşağı yönlü momentum daha güçlüdür.
        Aşırı Alım ve Aşırı Satım Bölgeleri:

        +50 ve üzeri değerler genellikle aşırı alım bölgesi olarak kabul edilir ve fiyatların bir düzeltme yapabileceğine işaret edebilir.
        -50 ve altındaki değerler aşırı satım bölgesi olarak kabul edilir ve fiyatların toparlanma eğiliminde olabileceğine işaret edebilir.
        
        """
        return df

    def stokastik(df, k_period=14, d_period=3):
        """
            Yorumlama

            Overbought (Aşırı Alım) ve Oversold (Aşırı Satım) Durumları:
                %K ve %D çizgileri 80'in üzerinde olduğunda, aşırı alım durumuna işaret edebilir ve fiyatın geri çekilebileceğini gösterir.
                %K ve %D çizgileri 20'nin altında olduğunda, aşırı satım durumuna işaret edebilir ve fiyatın yukarı dönebileceğini gösterir.

            Çizgi Kesişimleri:
                %K çizgisi %D çizgisini yukarıdan keserse, bu bir satış sinyali olabilir.
                %K çizgisi %D çizgisini aşağıdan yukarıya keserse, bu bir alım sinyali olabilir.
        """
        # 'df' DataFrame'inin 'high', 'low' ve 'close' kolonlarına sahip olduğunu varsayıyoruz.
        isim_k = f'k_{k_period}'
        isim_d = f'd_{d_period}'
        # En yüksek ve en düşük değerleri hesapla
        df['Lowest_Low'] = df['low'].rolling(window=k_period).min()
        df['Highest_High'] = df['high'].rolling(window=k_period).max()
        
        # %K ve %D değerlerini hesapla
        df[isim_k] = 100 * ((df['close'] - df['Lowest_Low']) / (df['Highest_High'] - df['Lowest_Low']))
        df[isim_d] = df[isim_k].rolling(window=d_period).mean()
        
        # Gereksiz kolonları kaldır
        df.drop(['Lowest_Low', 'Highest_High'], axis=1, inplace=True)
        
        return df

        """
            Stochastic Oscillator’ın Birlikte Kullanılabileceği Diğer Göstergeler

            Göreceli Güç Endeksi (RSI):
                Amaç: Hem RSI hem de Stochastic Oscillator aşırı alım ve aşırı satım bölgelerini tanımlamak için kullanılır. Ancak, RSI daha genel bir momentum göstergesidir ve trendleri izlemek için biraz daha sağlamdır.
                Kombinasyon Faydası: Her iki gösterge de aşırı alım veya satım sinyali verdiğinde, sinyal daha güvenilir hale gelir. Örneğin, RSI 70'in üzerinde ve Stochastic Oscillator %K ve %D çizgileri 80'in üzerinde ise güçlü bir satış sinyali olabilir.

            Hareketli Ortalama Yakınsama Iraksama (MACD):
                Amaç: MACD, trend dönüş noktalarını belirlemek için kullanılan bir momentum ve trend göstergesidir. Fiyatın mevcut trendini ve trendin gücünü analiz eder.
                Kombinasyon Faydası: MACD, genel trend yönünü doğrularken, Stochastic Oscillator kısa vadeli aşırı alım ve satım sinyalleri sağlar. MACD yükselişteyse ancak Stochastic aşırı satım bölgesindeyse, bu, trend yönünde alım fırsatı olabilir.

            Hareketli Ortalamalar (MA veya EMA):
                Amaç: Hareketli ortalamalar, fiyatın genel yönünü gösterir ve uzun vadeli trend analizi için kullanılır.
                Kombinasyon Faydası: Stochastic Oscillator aşırı alım veya satım bölgesindeyken fiyat, hareketli ortalamanın altındaysa, trendin yönüyle birlikte güçlü bir alım veya satım sinyali oluşabilir. Örneğin, Stochastic aşırı satımda ve fiyat 50 günlük EMA'nın üzerindeyse, trend yönünde alım fırsatı olabilir.

            Bollinger Bantları:
                Amaç: Bollinger Bantları, fiyatın ortalamasından ne kadar sapmış olduğunu analiz eder ve fiyatın aşırı oynaklık gösterdiği veya konsolidasyon aşamasında olduğunu gösterir.
                Kombinasyon Faydası: Fiyat Bollinger Bantlarının dışına taşarken Stochastic Oscillator aşırı alım veya satım sinyali veriyorsa, fiyatın tersine döneceği tahmin edilebilir. Örneğin, fiyat üst banda yakınken Stochastic aşırı alım sinyali veriyorsa, fiyatın düşme ihtimali artabilir.

            Parabolic SAR (Stop and Reverse):
                Amaç: Parabolic SAR, fiyatın tersine dönme potansiyeline işaret eden bir trend göstergesidir. Fiyatın altına ve üstüne nokta yerleşimleri ile trend dönüş sinyalleri verir.
                Kombinasyon Faydası: Stochastic Oscillator, kısa vadeli aşırı alım ve satım noktalarını gösterirken, Parabolic SAR fiyatın uzun vadeli yönü hakkında bilgi verir. Stochastic aşırı satımdayken SAR noktasının fiyatın altına geçmesi, alım sinyali için iyi bir doğrulama olabilir.

            Ortalama Yönsel Endeks (ADX):
                Amaç: ADX, trendin gücünü ölçer, ancak yön hakkında bilgi vermez. Bu nedenle, güçlü bir trendin var olup olmadığını belirlemek için kullanılır.
                Kombinasyon Faydası: Stochastic Oscillator, kısa vadeli aşırı alım veya satım sinyalleri verirken, ADX trendin gücünü doğrular. ADX 25'in üzerinde ve Stochastic aşırı alımda olduğunda, trend güçlü bir yükseliş trendiyse bile küçük bir geri çekilme yaşanabilir.

        Stochastic Oscillator ile Çoklu Göstergeler Kullanımı

        Bu göstergeleri bir arada kullanarak, çok daha sağlam ticaret stratejileri oluşturulabilir. Örneğin:

            RSI + Stochastic + MACD Kombinasyonu: RSI ve Stochastic ile aşırı alım veya satım bölgelerini belirledikten sonra, MACD sinyallerini izleyerek trend yönüne göre alım veya satım işlemi yapılabilir.
            Hareketli Ortalamalar + Stochastic + ADX Kombinasyonu: Fiyat bir hareketli ortalamanın altındaysa ve Stochastic aşırı alım gösteriyorsa, ADX de yüksekse, bu güçlü bir satış sinyali olabilir.
            
        UYARI:
            Genel Strateji ve Risk Yönetimi

            Birden fazla göstergenin aynı yönde sinyal verdiği durumlarda işlem yapmak daha güvenilir olabilir. Ancak, Stochastic Oscillator gibi kısa vadeli göstergelerin özellikle hızlı sinyaller verdiği unutulmamalıdır. Bu nedenle, stop-loss kullanarak riski sınırlamak ve sadece bir göstergenin sinyaline güvenmeden daha kapsamlı bir analiz yapmak her zaman iyi bir yaklaşımdır.
        """

    def williams_r(data, period=14):
        """
        Williams %R göstergesini hesaplayan fonksiyon.
        
        Parameters:
            data (DataFrame): Kapanış, en yüksek ve en düşük fiyat kolonlarına sahip veri.
            period (int): Gösterge için kullanılacak dönem (genelde 14'tür).
            
        Returns:
            pandas.Series: William %R göstergesinin hesaplanan değerleri.
        """
        
        isim_will_r = f'will_r_{period}'
        # Belirtilen periyottaki en yüksek ve en düşük değerleri hesapla
        high_max = data['High'].rolling(window=period).max()
        low_min = data['Low'].rolling(window=period).min()

        # William %R formülünü uygula
        data[isim_will_r] = ((high_max - data['Close']) / (high_max - low_min)) * -100
        
        return data

        """
        1. Göreceli Güç Endeksi (RSI)

            Nasıl Kullanılır: RSI, aşırı alım ve aşırı satım seviyelerini gösterir (%30’un altı aşırı satım, %70’in üstü aşırı alım olarak kabul edilir). William %R ve RSI, birbirleriyle benzer işlev görse de, farklı matematiksel yapıları sayesinde aşırı alım veya satım seviyelerini doğrulamak için kullanılabilirler.
            Sinyal: Hem William %R hem de RSI aynı anda aşırı alım veya aşırı satım bölgesindeyse, bu bölgedeki gücü doğrular ve tersine dönüş ihtimalini artırır.

        2. Hareketli Ortalama (MA veya EMA)

            Nasıl Kullanılır: Hareketli ortalamalar, fiyatın genel trendini gösterir. William %R ile birlikte hareketli ortalamalar, bir trendin güçlü olup olmadığını veya tersine dönüş sinyalini doğrulamak için kullanılabilir.
            Sinyal: William %R aşırı alım veya satım bölgesine girdiğinde, kısa dönem EMA’lar (örneğin, 20 günlük EMA) uzun dönem EMA’ların (örneğin, 50 günlük EMA) üzerinde ise (yükseliş trendi), trendin güçlü olduğunu gösterebilir. Tam tersi durumda ise düşüş trendi doğrulanmış olur.

        3. Hareketli Ortalama Yakınsama Iraksama (MACD)

            Nasıl Kullanılır: MACD, trendin gücünü ve momentumunu ölçmek için kullanılır. Özellikle MACD sinyal çizgisini geçtiğinde, bu trendin hızlanacağına dair bir işaret olabilir. William %R’nin verdiği aşırı alım veya satım sinyalleri ile MACD sinyalleri aynı anda gerçekleşiyorsa, bu güçlü bir dönüş sinyalidir.
            Sinyal: Örneğin, William %R aşırı satım bölgesinden yukarı çıkarken, MACD sinyal çizgisini yukarı kesiyorsa, bu güçlü bir alım sinyali olabilir.

        4. Bollinger Bantları

            Nasıl Kullanılır: Bollinger Bantları, fiyatın normal aralık dışına çıkıp çıkmadığını gösterir. Fiyat üst banda yakınken William %R aşırı alım bölgesindeyse, bu durumda fiyatın geri çekilme ihtimali yüksektir. Tam tersi durumda fiyat alt banda yakınken William %R aşırı satım bölgesindeyse, bu bir toparlanma işareti olabilir.
            Sinyal: Fiyat Bollinger Bantlarının üstüne veya altına temas ederken William %R aşırı alım veya satım bölgesinde bulunuyorsa, bu güçlü bir tersine dönüş sinyali olarak yorumlanabilir.

        5. Göreceli Hacim İndeksi (OBV veya Hacim Profili)

            Nasıl Kullanılır: On-Balance Volume (OBV), işlem hacmine göre fiyat hareketlerinin yönünü anlamaya yardımcı olur. William %R aşırı alım veya aşırı satım bölgesindeyken OBV'de de bir yükseliş veya düşüş gözlemlenirse, bu durum göstergede oluşan sinyali destekler.
            Sinyal: Örneğin, William %R aşırı satım bölgesindeyken OBV yükseliyorsa, hacmin toparlanma sinyalini desteklediği anlaşılabilir.

        6. Stokastik Osilatör

            Nasıl Kullanılır: Stokastik Osilatör, fiyatın kapanışını belirli bir dönemdeki yüksek-düşük aralığa göre gösterir. William %R ve Stokastik Osilatör birbirine benzese de, farklı matematiksel hesaplamalarla elde edildikleri için bir arada kullanıldıklarında güvenilir sinyaller verirler.
            Sinyal: Her iki gösterge de aşırı alım veya aşırı satım bölgesine aynı anda girip çıkıyorsa, bu güçlü bir alım veya satım sinyali olarak düşünülebilir.

        7. ADX (Ortalama Yön Endeksi)

            Nasıl Kullanılır: ADX, bir trendin ne kadar güçlü olduğunu gösterir. ADX değeri yüksek olduğunda, William %R’nin aşırı alım veya aşırı satım sinyali daha fazla güven verir. Ancak ADX düşükse (genellikle 20’nin altında), bu durumda William %R’nin verdiği sinyaller daha az güvenilirdir çünkü piyasa yatay hareket edebilir.
            Sinyal: ADX yüksekken (30’un üzerinde), William %R aşırı satım veya aşırı alım bölgesindeyse bu sinyale daha fazla güvenilebilir. ADX düşükken ise piyasanın yönsüz hareket edebileceği dikkate alınmalıdır.

        Özet

        William %R'nin gücünü artırmak ve yanlış sinyalleri azaltmak için:

            RSI ile aşırı alım/satım doğrulaması,
            MACD veya Hareketli Ortalama ile trend doğrulaması,
            Bollinger Bantları ile fiyat aralığı kontrolü,
            ADX ile trend gücü değerlendirmesi yaparak kullanabilirsiniz.

        Birden fazla göstergeyi kullanarak William %R’nin verdiği sinyalleri daha güvenilir hale getirebilirsiniz. Bu kombinasyonlar, özellikle risk yönetiminde daha dengeli ve stratejik hamleler yapmanıza olanak tanır.
        """

    #   Bunun kıvan versiyonunu incele
    def awesome_oscillator_with_signal(data, fastperiod=5, slowperiod=34, signalperiod=7):
        # Tipik fiyatı (high + low) / 2 olarak hesapla
        data['hl2'] = (data['high'] + data['low']) / 2
        
        isim_ao = f'ao_{fastperiod}_{slowperiod}_{signalperiod}'
        isim_ao_signal = f'ao_signal_{fastperiod}_{slowperiod}_{signalperiod}'
        # Hızlı ve yavaş SMA hesapla
        fast_ma = data['hl2'].rolling(window=fastperiod).mean()
        slow_ma = data['hl2'].rolling(window=slowperiod).mean()
        
        # Awesome Oscillator hesapla
        data[isim_ao] = fast_ma - slow_ma
        data.drop(['hl2'])
        # Sinyal çizgisi hesapla
        data[isim_ao_signal] = data[isim_ao].rolling(window=signalperiod).mean()
        
        return data

        """
            Awesome Oscillator’ın Yapısı ve Hesaplama Amacı

            Kısa ve Uzun Vadeli Hareketli Ortalamalar:
                AO, kısa vadeli (örneğin, 5 periyot) ve uzun vadeli (örneğin, 34 periyot) basit hareketli ortalamalar (SMA) arasındaki fark olarak hesaplanır.
                Tipik fiyat (yüksek + düşük) / 2 üzerinden hesaplanan bu hareketli ortalamalar, fiyatın yönelimi ve momentumu hakkında daha net bir bakış sunar.

            Farkı Ölçme:
                Kısa vadeli SMA, mevcut fiyatın daha hızlı değişimlerini gösterirken, uzun vadeli SMA, daha geniş bir süre zarfındaki fiyat eğilimini gösterir.
                AO değeri, kısa vadeli ve uzun vadeli momentum arasındaki farkı ölçer. Kısa SMA uzun SMA’nın üzerindeyse pozitif, altındaysa negatif olur.

            Sinyal Çizgisi (Opsiyonel):
                AO üzerine bir sinyal çizgisi (örneğin, AO’nun 7 periyotluk SMA’sı) eklenebilir. Bu çizgi, AO’nun daha yumuşak bir versiyonudur ve al-sat sinyalleri oluşturmak için kullanılır.

        Awesome Oscillator Kullanımı ve Sinyaller

        AO değerleri ve sinyal çizgisi, piyasa katılımcılarına belirli sinyaller verir:

            Sıfır Çizgisi Geçişleri:
                AO, sıfır çizgisini yukarıya geçerse bu, kısa vadeli momentumun yükselişe geçtiğini ve yükseliş trendinin güçlendiğini gösterir. Bu durumda alım sinyali alınabilir.
                AO, sıfır çizgisini aşağıya geçerse bu, kısa vadeli momentumun düşüşe geçtiğini ve düşüş trendinin güçlendiğini gösterir. Bu durumda satış sinyali alınabilir.

            İkili Tepe ve Dip Formasyonları (Double Peak):
                AO, sıfır çizgisinin üstünde iki tepe oluşturduğunda (çift tepe formasyonu) ve ikinci tepe birinciden düşükse, bu düşüş sinyali olarak kabul edilebilir.
                Sıfır çizgisinin altında iki dip oluştuğunda ve ikinci dip daha yüksekse bu, bir yükseliş sinyalidir.

            Sinyal Çizgisi Kesişimi:
                AO, sinyal çizgisini yukarıdan aşağıya keserse, momentum düşüş eğiliminde olabilir; bu durumda sat sinyali alınabilir.
                AO, sinyal çizgisini aşağıdan yukarıya keserse momentum yükseliyor olabilir; bu durumda al sinyali düşünülebilir.

        Awesome Oscillator’ın Kullanım Amacı

        AO, özellikle trend ve momentum stratejilerinde şu amaçlar doğrultusunda kullanılır:

            Trend Yönünü Belirleme: AO pozitif olduğunda, piyasanın genel olarak yükseliş yönünde olduğunu gösterir; negatif olduğunda ise düşüş trendi işaret eder.
            Dönüş Noktalarını Yakalama: Sıfır çizgisi geçişleri, momentumdaki yön değişikliklerine işaret eder. Bu geçişler, trendin yön değiştirdiği anlamına gelebilir.
            Alım ve Satım Sinyalleri Oluşturma: Sıfır çizgisi ve sinyal çizgisi kesişimleri al-sat sinyalleri verir.

        Awesome Oscillator, fiyatların kısa vadede uzun vadeye göre nasıl hareket ettiğini ve bunun hangi yönde bir ivme oluşturduğunu gösterir.
        """

    def tsi(df, long_period=25, short_period=13, signal_period=7):
        """
        DataFrame üzerinden True Strength Index (TSI) ve sinyal hattı hesaplama fonksiyonu.
        
        Parametreler:
        - df: Fiyat verilerini içeren pandas DataFrame
        - close_column: Kapanış fiyatlarının bulunduğu sütun adı (varsayılan: 'close')
        - long_period: Uzun EMA periyodu (varsayılan: 25)
        - short_period: Kısa EMA periyodu (varsayılan: 13)
        - signal_period: Sinyal hattı için EMA periyodu (varsayılan: 7)
        
        Dönüş:
        - TSI ve sinyal hattı değerlerini içeren pandas DataFrame
        """
        # TSI hesapla
        
        isim_tsi = f'tsi_{long_period}_{short_period}_{signal_period}'
        isim_tsi_sinyal = f'tsi_sinyal_{long_period}_{short_period}_{signal_period}'
        
        df[isim_tsi] = ta.momentum.tsi(df['close'], window_slow=long_period, window_fast=short_period)
        
        # Sinyal hattını TSI'ın EMA'sı olarak hesapla
        df[isim_tsi_sinyal] = df['tsi'].ewm(span=signal_period, adjust=False).mean()
        
        return df

        """
            TSI göstergesi ve onun sinyal hattı (TSI_Signal) ile sıfır çizgisi, bir trendin gücünü ve yönünü belirlemek için birlikte değerlendirilir. Bu üç unsurun birbirleriyle olan konumları, piyasadaki potansiyel alım veya satım sinyallerini anlamada önemlidir.
        1. TSI ve Sinyal Çizgisi Kesişimleri

            Alım Sinyali (Pozitif Kesişim): TSI, sinyal hattını aşağıdan yukarıya doğru keserse bu, yükseliş momentumunun başladığını ve alım yapılabileceğini gösterir. Bu durumda, fiyat artışının devam edebileceği düşünülür.
            Satım Sinyali (Negatif Kesişim): TSI, sinyal hattını yukarıdan aşağıya doğru keserse bu, düşüş momentumunun başladığını ve satım yapılabileceğini gösterir. Bu durumda, fiyat düşüşünün devam edebileceği düşünülür.

        2. TSI ve Sıfır Çizgisi Kesişimleri

            Pozitif Bölgeye Geçiş (Sıfırın Üzerine Çıkma): TSI sıfır çizgisinin üzerine çıkarsa bu, genel olarak yukarı yönlü trendin başladığını veya gücünü koruduğunu gösterir. Bu durum piyasanın alıcılı olduğuna işaret eder.
            Negatif Bölgeye Geçiş (Sıfırın Altına İnme): TSI sıfır çizgisinin altına düşerse bu, genel olarak aşağı yönlü trendin başladığını veya devam ettiğini gösterir. Bu durumda piyasanın satıcılı olduğu düşünülebilir.

        3. TSI, TSI_Signal ve Sıfır Çizgisi ile Birlikte Yorumlama

            Güçlü Alım Sinyali: TSI, sıfır çizgisinin üzerinde iken sinyal hattını aşağıdan yukarıya doğru kesiyorsa, bu güçlü bir alım sinyalidir. Bu durumda, yukarı yönlü momentum hem sinyal hattı hem de sıfır çizgisi tarafından desteklenir, dolayısıyla fiyat artışının devam etme olasılığı yüksektir.

            Güçlü Satım Sinyali: TSI, sıfır çizgisinin altında iken sinyal hattını yukarıdan aşağıya doğru kesiyorsa, bu güçlü bir satım sinyalidir. Bu durumda, düşüş yönlü momentum hem sinyal hattı hem de sıfır çizgisi tarafından desteklenir, dolayısıyla fiyat düşüşünün devam etme olasılığı yüksektir.

            Trendin Zayıflaması: TSI pozitif bölgede (sıfır çizgisinin üzerinde) ancak sinyal hattının altında ise, yukarı yönlü trendin zayıfladığına işaret edebilir. Bu durumda, bir geri çekilme yaşanabilir veya fiyat konsolidasyon sürecine girebilir.

            Trendin Tersine Dönüş İhtimali: TSI negatif bölgede (sıfır çizgisinin altında) ancak sinyal hattının üzerinde ise, aşağı yönlü trendin zayıfladığına işaret eder. Bu durumda, bir toparlanma yaşanabilir veya fiyat bir yükseliş trendine geçebilir.

        Özet Strateji

            Alım Kararı:
                TSI sinyal hattını yukarı kesiyor ve sıfır çizgisinin üstünde.
                Bu durumda piyasa yukarı yönlü momentum ile destekleniyor ve fiyatın artabileceği düşünülüyor.

            Satım Kararı:
                TSI sinyal hattını aşağı kesiyor ve sıfır çizgisinin altında.
                Bu durumda piyasa aşağı yönlü momentum ile destekleniyor ve fiyatın düşüşe geçebileceği düşünülüyor.

            Trendi Takip Etme:
                TSI ve sinyal hattı sıfır çizgisinin üstünde ve TSI sinyal hattının üstünde ise yukarı trend güçlüdür.
                TSI ve sinyal hattı sıfır çizgisinin altında ve TSI sinyal hattının altında ise aşağı trend güçlüdür.

        Bu şekilde TSI, TSI_Signal ve sıfır çizgisi ile fiyat hareketlerinin yönünü ve momentumunu değerlendirebilir, daha bilinçli alım-satım kararları alabilirsiniz.
        """
        
        
        """
        TSI --- RSI KARŞILAŞTIRMASI
        
            TSI (True Strength Index) ve RSI (Relative Strength Index), her ikisi de fiyat hareketlerinin momentumunu ölçen ve alım-satım sinyalleri üreten teknik göstergelerdir. Ancak, hesaplama yöntemleri, hassasiyetleri ve kullanım amaçları açısından bazı temel farklar vardır:
        1. Hesaplama Yöntemi

            RSI: RSI, kapanış fiyatlarının belirli bir dönemdeki yukarı ve aşağı yönlü hareketlerinin oranını ölçer. Genellikle 14 dönemlik bir hesaplama yapılır ve sonuç 0-100 arasında bir değerdir. RSI, fiyatın yukarı veya aşağı yönlü hareketlerinin gücünü basit bir matematiksel formül ile hesaplar.

            TSI: TSI, fiyatın değişimlerini iki aşamalı bir üssel hareketli ortalama (EMA) süzgecinden geçirerek daha uzun vadeli bir momentum göstergesi oluşturur. İlk olarak, fiyatın günlük değişimi hesaplanır ve ardından bu değişimler iki kez EMA'ya tabi tutulur. Bu iki katmanlı EMA, göstergenin daha pürüzsüz ve yavaş hareket etmesini sağlar.

        2. Gecikme ve Duyarlılık

            RSI: RSI, fiyat dalgalanmalarına daha hızlı tepki verir ve kısa vadeli değişiklikleri yakalama konusunda oldukça iyidir. Bu nedenle RSI, hızlı sinyaller üretir ancak bazen daha fazla yanlış sinyal verebilir, özellikle yüksek volatilite dönemlerinde.

            TSI: TSI, iki EMA katmanına dayandığı için fiyat dalgalanmalarına daha yavaş tepki verir. Bu durum, TSI’nın uzun vadeli trendleri ve genel momentum değişimlerini takip etmekte daha etkili olmasını sağlar. TSI, kısa vadeli dalgalanmalara karşı daha az hassastır ve daha az yanlış sinyal üretir, ancak daha uzun vadeli bir bakış açısı sunar.

        3. Sinyal Üretme ve Kullanım Alanları

            RSI: RSI değeri genellikle 70'in üzerinde olduğunda "aşırı alım" ve 30'un altında olduğunda "aşırı satım" olarak yorumlanır. Bu durumlar, olası bir trend dönüşüne veya düzeltmeye işaret edebilir. RSI, hızlı değişimlere yanıt vermesi sayesinde aşırı alım ve aşırı satım seviyelerinin hızlı tespitinde kullanılır ve kısa vadeli alım-satım kararları için uygundur.

            TSI: TSI, sinyal hattı ve sıfır çizgisi kesişimleri ile alım ve satım sinyalleri sağlar. Sıfır çizgisinin üstüne çıkması yükseliş momentumunu, altına inmesi ise düşüş momentumunu gösterir. TSI ayrıca trendin yönünü ve gücünü anlamak için daha uzun vadeli bir gösterge olarak kullanılır. Bu nedenle, TSI genellikle trend takibi ve genel momentum analizi için tercih edilir.

        4. Aşırı Alım ve Aşırı Satım Bölgeleri

            RSI: RSI, belirli bir üst ve alt sınırda (70 ve 30) aşırı alım ve aşırı satım sinyalleri üretir. Bu sınır seviyeleri, RSI’nın kullanımında standarttır ve birçok teknik analist bu seviyeleri baz alarak karar verir.

            TSI: TSI için standart bir aşırı alım veya aşırı satım seviyesi bulunmamaktadır. Ancak bazı yatırımcılar, TSI’yı aşırı alım/aşırı satım aracı olarak kullanmak için +25 ve -25 gibi seviyeler belirleyebilir. Bu sınırlar RSI kadar yaygın olarak kullanılmaz, çünkü TSI daha çok trend takibi için tasarlanmıştır.

        5. Trendin Gücünü Anlama

            RSI: RSI, aşırı alım ve aşırı satım seviyeleri ile daha çok trendin tersine dönmesi veya düzeltme yapması gereken noktaları bulmaya odaklanır. Trendin gücünü anlamak için doğrudan bir bilgi sunmaz.

            TSI: TSI, trendin gücünü ve devamlılığını anlamak için sıfır çizgisini kullanır. Sıfırın üzerinde veya altında bulunması, trendin yukarı veya aşağı yönlü olduğunu ve bu trendin gücünü koruyup korumadığını gösterir. Bu nedenle TSI, trendin devamlılığını anlamada RSI’dan daha etkilidir.

        Özet

            RSI: Daha hızlı, kısa vadeli aşırı alım ve aşırı satım sinyalleri vermek için tasarlanmış bir momentum göstergesidir. Dönüş sinyalleri veya hızlı tepki arayan yatırımcılar için uygundur.
            TSI: Daha yavaş, daha uzun vadeli bir momentum göstergesidir ve trendin devamlılığını veya gücünü ölçmek için kullanılır. Trend takibi ve genel momentum analizi yapan yatırımcılar için daha uygundur.

        Bu farklılıkları göz önünde bulundurarak, her iki göstergenin de farklı koşullarda kullanılmasını öneririm. Örneğin, RSI kısa vadeli alım-satım kararları için, TSI ise uzun vadeli trend takibi için kullanılabilir.
        """

    def ppo(df, slow_period=26, fast_period=12, signal_period=9):
        
        """
        PPO (Percentage Price Oscillator) hesaplayan fonksiyon.

        Args:
            df (pd.DataFrame): 'close' sütununu içeren veri.
            window_slow (int): Yavaş EMA için periyot.
            window_fast (int): Hızlı EMA için periyot.
            window_sign (int): Sinyal hattı için periyot.
            
            ppo: PPO değeri,
            ppo_signal: Sinyal hattı (örneğin, 9 periyotlu EMA),
            ppo_hist: PPO ve sinyal hattı arasındaki farktır.

        Returns:
            pd.DataFrame: PPO, PPO sinyali ve PPO histogram sütunlarını içeren DataFrame.
        """
        
        isim_slow = f'ppo_slow_{slow_period}'
        isim_fast = f'ppo_fast_{fast_period}'
        isim_sinyal = f'ppo_signal_{signal_period}'
        
        ppo_indicator = ta.momentum.PPOIndicator(close=df['close'], window_slow=slow_period, window_fast=fast_period, window_sign=signal_period)
        df[isim_slow] = ppo_indicator.ppo()
        df[isim_fast] = ppo_indicator.ppo_signal()
        df[isim_sinyal] = ppo_indicator.ppo_hist()
        
        return df

        """
            PPO (Percentage Price Oscillator), iki farklı periyottaki üstel hareketli ortalamalar (EMA) arasındaki yüzdesel farkı gösteren bir osilatördür. PPO, trend gücünü ölçmek ve alım-satım sinyalleri üretmek için kullanılır. İşte PPO'nun nasıl yorumlanabileceğine dair bazı önemli noktalar:
            1. PPO ve PPO Sinyal Hattının Kesişimi

                PPO Sinyal Hattı (9 günlük EMA): PPO değerinin belirli bir periyot için (genellikle 9) EMA’sıdır ve kısa vadeli trend yönünü gösterir.
                Al Sinyali: PPO hattı (hızlı EMA) sinyal hattını (yavaş EMA) yukarı doğru kesiyorsa, bu bir yükseliş sinyali olarak kabul edilir. Bu durumda piyasa yukarı yönlü bir hareket gösterebilir.
                Sat Sinyali: PPO hattı, sinyal hattını aşağı doğru kesiyorsa, bu düşüş sinyali olarak kabul edilir. Bu durumda piyasa aşağı yönlü bir hareket gösterebilir.

            2. PPO Histogramı

                PPO Histogramı: PPO hattı ile sinyal hattı arasındaki farktır ve histogram şeklinde gösterilir. Histogram pozitif ise yükseliş ivmesi güçlü, negatif ise düşüş ivmesi güçlüdür.
                Histogramın Pozitiften Negatife Geçmesi: Yukarı yönlü ivmenin zayıfladığını ve olası bir düşüş eğilimini gösterir.
                Histogramın Negatiften Pozitife Geçmesi: Aşağı yönlü ivmenin zayıfladığını ve yükseliş eğiliminin başlayabileceğini gösterir.

            3. PPO Değerinin Yüksekliği veya Düşüklüğü

                Pozitif PPO: PPO değeri pozitif olduğunda, hızlı EMA yavaş EMA'nın üzerindedir, bu da yükseliş eğiliminde olunduğuna işaret eder.
                Negatif PPO: PPO değeri negatif olduğunda, hızlı EMA yavaş EMA'nın altındadır, bu da düşüş eğiliminde olunduğunu gösterir.
                PPO Değerinin Büyük Olması: PPO değeri büyükse, EMA'lar arasındaki fark geniştir; bu, güçlü bir trendi gösterir.
                PPO Değerinin Küçük Olması: PPO değeri küçükse, EMA'lar birbirine yakındır; bu, trendin zayıf veya yatay bir seyir izlediğini gösterebilir.

            4. Aşırı Alım ve Aşırı Satım

            PPO değerleri, aşırı alım veya aşırı satım koşullarını belirlemek için kullanılabilir, ancak genellikle bu göstergede kesin sınırlar yoktur. Yüksek pozitif PPO değerleri piyasanın aşırı alımda, düşük negatif PPO değerleri ise piyasanın aşırı satımda olabileceğine işaret edebilir.
            5. Uyumsuzluklar (Divergence)

                Pozitif Uyumsuzluk: Fiyat düşerken PPO yükseliyorsa, bu pozitif bir uyumsuzluktur ve fiyatın yön değiştirebileceğine işaret edebilir.
                Negatif Uyumsuzluk: Fiyat yükselirken PPO düşüyorsa, bu negatif bir uyumsuzluktur ve fiyatın düşebileceğine işaret edebilir.

            Özet

            PPO, trend gücünü ve yönünü belirlemek için kullanılan çok yönlü bir osilatördür. PPO sinyal hattı ile PPO arasındaki kesişimler ve histogramın pozitif ya da negatif olması, trendin yönü hakkında bilgi verir. Ayrıca uyumsuzluklar, olası trend dönüşleri hakkında ipuçları sunar.
        """

    def roc(df, period=14,):
        """
        Rate of Change (ROC) indikatörünü hesaplar.
        
        Parameters:
        - df (pd.DataFrame): Fiyat verilerini içeren DataFrame.
        - period (int): Hesaplama periyodu, varsayılan 14.
        - column (str): Değişim oranı hesaplanacak kolon, varsayılan 'close'.

        Returns:
        - pd.Series: ROC değerleri.
        """
        
        isim_roc = f'roc_{period}'
        roc_indicator = ta.momentum.ROCIndicator(close=df['close'], window=period)
        df[isim_roc] = roc_indicator.roc()
        return df

        """
               ROC İLE MOMENTUM ARASINDAKİ FARKLILIKLAR
        Özellik	    Momentum	                            Rate of Change (ROC)
        Tanım	    Fiyat farkını ölçer	                    Fiyat farkını yüzde olarak ifade eder
        Formül	    Mevcut Fiyat−N do¨nem o¨nceki Fiyat     Mevcut Fiyat−N do¨nem o¨nceki Fiyat	100×Fiyat FarkıO¨nceki 
                                                            Fiyat100×O¨nceki FiyatFiyat Farkı​
        Birimi	    Fiyat (örneğin, USD)	                Yüzde (%)
        Hassasiyet	Daha ham bir gösterge	                Normalleştirilmiş bir gösterge
        
            ROC (Rate of Change) indikatörü, fiyat hareketlerinin hızını ölçen bir momentum indikatörüdür. Belirli bir dönem için yüzdesel olarak fiyat değişimini gösterir ve trendin gücü hakkında bilgi sağlar. ROC'yi yorumlarken dikkate alınması gereken başlıca noktalar şunlardır:

            Pozitif ve Negatif Değerler:
                ROC pozitif olduğunda, fiyatların önceki döneme göre yükseldiği anlamına gelir. Pozitif ROC değeri ne kadar yüksekse, fiyat artışı o kadar güçlüdür.
                ROC negatif olduğunda, fiyatların önceki döneme göre düştüğü anlamına gelir. Negatif ROC değeri ne kadar düşükse, fiyat düşüşü o kadar güçlüdür.

            0 Çizgisi (Merkez Çizgisi):
                ROC, 0 çizgisinin üzerine çıktığında, bu, fiyatın önceki döneme göre arttığını ve bir yükseliş trendinin olabileceğini gösterir.
                ROC, 0 çizgisinin altına düştüğünde, bu, fiyatın önceki döneme göre azaldığını ve düşüş trendinin başladığını gösterebilir.
                0 çizgisi, trend değişimlerinde kritik bir referans noktası olarak kullanılabilir.

            Aşırı Alım ve Aşırı Satım Durumları:
                ROC, çok yüksek pozitif değerlere ulaştığında aşırı alım (overbought) durumunu gösterebilir. Bu durumda fiyatın düzeltilmesi veya bir geri çekilme yaşanması olasılığı vardır.
                Çok düşük negatif değerlere ulaştığında ise aşırı satım (oversold) durumu olarak yorumlanabilir. Bu durumda fiyatın toparlanması veya yükselmesi beklenebilir.
                Aşırı alım/satım seviyeleri, genellikle tarihsel ROC değerlerine göre belirlenir ve her varlık için farklı olabilir.

            Diverjans (Uyumsuzluk):
                Fiyat yükselirken ROC düşüyorsa, bu durum momentumun zayıfladığına işaret edebilir ve trendde bir dönüş sinyali olarak yorumlanabilir.
                Benzer şekilde, fiyat düşerken ROC yükseliyorsa, bu da düşüş trendinin zayıfladığına ve olası bir dönüşe işaret edebilir.

            ROC ve Diğer İndikatörlerin Birlikte Kullanımı:
                Tek başına ROC sinyalleri her zaman güvenilir olmayabilir. Bu yüzden ROC genellikle trend göstergeleri (örneğin EMA) veya osilatörlerle (örneğin RSI) birlikte kullanılır.
                Örneğin, ROC’nin 0 çizgisinin üzerine çıkması ve aynı zamanda bir hareketli ortalama kesişmesi, daha güçlü bir alım sinyali verebilir.

            ---  ÖNEMLİ UYARI  ---
        ROC indikatörü, özellikle hızlı fiyat hareketlerinde etkili olsa da, yatay piyasalarda yanıltıcı sinyaller üretebilir. Bu yüzden belirli bir periyot ve eşik seviyeleri belirleyerek test etmek ve diğer analiz araçlarıyla desteklemek faydalı olabilir.
        """

    def momentum_ta(df, short_period=5, long_period=10, avg_period=14):
        # 5 periyodluk momentum hesaplama
        isim_kisa = f'momentum_kisa_{short_period}'
        isim_uzun = f'momentum_uzun_{long_period}'
        isim_ortalama = f'momentum_ortalama_{avg_period}'
        df[isim_kisa] = ta.momentum.ROCIndicator(close=df['close'], window=short_period).roc()
        
        # 10 periyodluk momentum hesaplama
        df[isim_uzun] = ta.momentum.ROCIndicator(close=df['close'], window=long_period).roc()
        
        # Ortalama momentum çizgisi (son 14 periyodun ortalaması)
        df[isim_ortalama] = df[[isim_kisa, isim_uzun]].mean(axis=1).rolling(window=avg_period).mean()
        
        return df
        """
            Momentum göstergesi, fiyatın belirli bir süre boyunca ne kadar hızlı değiştiğini ölçerek piyasanın hızını ve yönünü anlamaya yardımcı olur. Bu göstergede temel yorumlar şunlardır:
        1. Pozitif ve Negatif Değerler

            Pozitif Momentum: Momentum değeri pozitif olduğunda, fiyatların artma eğiliminde olduğunu gösterir. Yani, yükseliş trendi güçleniyor olabilir.
            Negatif Momentum: Momentum değeri negatif olduğunda, fiyatların düşüş eğiliminde olduğunu gösterir. Bu, düşüş trendinin hızlandığını işaret edebilir.

        2. Momentumun Sıfır Noktası Etrafında Dönmesi

            Sıfır Çizgisi Üzerinde: Momentum değeri sıfırın üzerinde olduğunda, fiyatın önceki belirlenen periyoda göre daha yüksek olduğunu ve yükseliş trendinin devam ettiğini gösterir.
            Sıfır Çizgisi Altında: Momentum değeri sıfırın altına düştüğünde, fiyatın düşüş trendinde olduğunu gösterir. Bu durumda, fiyatlar önceki periyoddan daha düşük seviyelerdedir.

        3. Momentumun Artış ve Azalışları

            Momentum Artıyorsa: Göstergede momentum değerlerinin artması, trendin güçlendiğine işaret eder. Yükseliş trendinde momentumun artması, trendin sağlamlaştığını gösterir.
            Momentum Azalıyorsa: Momentum değerlerinin düşmesi, trendin zayıfladığı anlamına gelir. Örneğin, yükseliş trendinde momentum düşüyorsa, bu trendin sona erebileceğine veya kısa vadeli bir düzeltme olabileceğine işaret eder.

        4. Çift Periyot ve Ortalama Momentum Yorumlaması

            Kısa Periyot ile Uzun Periyodun Kesimi: Kısa periyotlu momentum değeri (örneğin 5 periyot) uzun periyotlu momentum değerini (örneğin 10 periyot) yukarı doğru keserse bu, kısa vadeli bir güçlenme ve olası bir alım sinyali olabilir.
            Uzun Periyodun Kısa Periyodu Kesmesi: Uzun periyotlu momentum değeri, kısa periyodu aşağı doğru kesiyorsa, bu durumda kısa vadeli zayıflama sinyali alınır ve satış sinyali olarak değerlendirilebilir.
            Ortalama Momentum: Son 14 periyodun ortalaması olarak hesaplanan momentum değeri, genel trendin gücünü anlamak için referans çizgisi olarak kullanılır. Ortalama momentum değeri yukarı yönlü ise piyasada ivme artışı, aşağı yönlü ise ivme kaybı olabilir.

        5. Aşırı Alım ve Aşırı Satım Durumları

            Aşırı Alım: Momentum aşırı yüksek seviyelere çıkarsa, bu fiyatların kısa vadede çok fazla yükseldiğini gösterebilir ve bir düzeltme yaşanabilir. Momentum göstergesinin aşırı yüksek seviyelere çıkması, alım baskısının bir noktada tükeneceğine işaret eder.
            Aşırı Satım: Momentum çok düşük seviyelere inerse, bu, fiyatların çok fazla düştüğünü ve bir toparlanma ihtimali olduğunu gösterebilir.

        Bu yorumlar, momentum göstergesinin genel kullanım şekilleridir. Momentum, tek başına karar vermek için kullanılmaktan ziyade, diğer göstergelerle desteklenerek piyasa trendlerini daha sağlıklı anlamaya yardımcı olur.

        ---    AŞIRI ALIM VE SATIM NOKTALARI   ---

        Momentum göstergesi için aşırı alım ve aşırı satım noktaları, belirli seviyelerin üzerindeki veya altındaki değerleri işaret eder ve piyasanın potansiyel olarak aşırı alındığını veya satıldığını gösterir. Bu seviyeler, piyasaya ve analiz edilen varlığa göre değişiklik gösterebilir. Ancak genel olarak şu kriterler kullanılabilir:
        1. Momentum için Genel Aşırı Alım ve Aşırı Satım Seviyeleri

            Aşırı Alım (Overbought): Momentum değeri belirli bir pozitif seviyenin üzerine çıktığında, fiyatların aşırı alındığı kabul edilir ve bu seviye genellikle olası bir düzeltme veya geri çekilme sinyali olarak yorumlanır.
                Momentum göstergesinde aşırı alım seviyesi, genellikle +20 veya +25 seviyesinin üzeri olarak kabul edilir.
            Aşırı Satım (Oversold): Momentum değeri belirli bir negatif seviyenin altına düştüğünde, fiyatların aşırı satıldığı anlamına gelir ve bu, fiyatların toparlanma potansiyeline sahip olabileceğini gösterebilir.
                Aşırı satım seviyesi genellikle -20 veya -25 seviyesinin altı olarak kabul edilir.

        Bu seviyeler, momentumun referans çizgisi olan sıfır çizgisinden ne kadar uzakta olduğunu gösterir. Örneğin, +20 seviyesinin üzerine çıkmış bir momentum değeri, piyasanın aşırı alım bölgesinde olduğunu ve düzeltme potansiyelini artırabileceğini gösterir.
        2. Özelleştirilmiş Aşırı Alım ve Satım Seviyeleri

            Volatiliteye Bağlı Seviyeler: Eğer analiz edilen varlık yüksek volatiliteye sahipse, aşırı alım/satım seviyeleri daha geniş belirlenebilir. Düşük volatiliteye sahip varlıklarda ise bu seviyeler daha dar tutulabilir. Örneğin, volatil bir hisse senedinde +30 ve -30 seviyeleri tercih edilebilirken, daha durağan bir hisse için +15 ve -15 seviyeleri kullanılabilir.
            Geçmiş Verilere Göre Uyarlama: Her varlığın tarihsel verilerine göre aşırı alım ve satım seviyeleri uyarlanabilir. Momentum göstergesinin önceki zirve ve dip noktaları incelenerek bu seviyeler özelleştirilebilir. Örneğin, belirli bir varlık daha önce +25 seviyesinde tepki verip düşüşe geçtiyse, bu seviyeyi aşırı alım noktası olarak almak mantıklı olabilir.

        3. Aşırı Alım ve Satım Yorumları

            Aşırı Alım Durumunda: Momentum aşırı alım seviyesine ulaştığında, fiyatların kısa vadede fazla yükselmiş olabileceği ve bir düzeltme veya kar satışı yaşanabileceği düşünülür. Bu, satış fırsatı veya varlığı elden çıkarma sinyali olarak yorumlanabilir.
            Aşırı Satım Durumunda: Momentum aşırı satım seviyesine düştüğünde, fiyatların çok fazla düşmüş olduğu ve toparlanma potansiyelinin arttığı anlamına gelir. Bu da alım fırsatı olarak değerlendirilebilir.

        Momentumun aşırı alım/satım bölgelerine ulaştığında diğer teknik göstergelerle doğrulama yapmak, yanlış sinyallerden kaçınmak için önemlidir.
        
        --------------------
        
        MOMEMTUM --- HACİM İLİŞKİSİ
        
                momentum ve hacim arasında güçlü bir ilişki vardır ve bu iki gösterge birlikte analiz edildiğinde piyasanın hareketleri hakkında daha sağlam bilgiler sağlar. Bu ilişki, özellikle fiyatların yönü ve bu yönün devam etme olasılığı hakkında fikir verir. İşte momentum ile hacim arasındaki ilişki ve nasıl yorumlanabileceğine dair bazı temel noktalar:
            1. Momentum Artışı ve Hacim Yükselişi

                Yüksek Momentum + Yüksek Hacim: Momentum göstergesi yüksek pozitif değerler gösterirken hacim de artıyorsa, bu durum, fiyatın yukarı yönlü hareketinin güçlü olduğunu ve yatırımcılar tarafından desteklendiğini gösterir. Genellikle trendin sağlam olduğunu ve yükselişin devam edebileceğini işaret eder.
                Düşüş Momentum + Yüksek Hacim: Momentum negatif bir yöne işaret ederken hacmin yüksek olması, güçlü bir satış baskısını gösterir. Bu durumda düşüş trendinin devam etme olasılığı yüksek olabilir.

            2. Momentum Artışı ve Düşük Hacim

                Yüksek Momentum + Düşük Hacim: Eğer momentum pozitif ve fiyat yükseliyor ancak hacim düşükse, bu yükselişin daha zayıf bir temele dayandığı anlamına gelebilir. Hacim desteği olmadan gerçekleşen bu tür yükselişler, sürdürülebilir olmayabilir ve hızlı bir düzeltme yaşanabilir.
                Düşüş Momentum + Düşük Hacim: Fiyatlar düşüyor ve momentum negatif olmasına rağmen hacim düşükse, düşüşün gücü zayıf olabilir ve trendin yakın zamanda değişebileceğine işaret edebilir.

            3. Hacim ve Momentum Uyumsuzluğu (Diverjans)

                Momentum ve Hacim Uyumsuzluğu: Eğer fiyatlar yükselirken momentum ve hacim düşmeye başlarsa, bu, trendin zayıfladığına dair bir uyarı olabilir. Bu tür uyumsuzluklar, fiyat trendinde potansiyel bir değişimin sinyalini verebilir. Örneğin, yükselen fiyatlar azalan momentum ve hacimle desteklenmiyorsa, bu yükselişin sonuna yaklaşıldığını veya bir geri çekilme olabileceğini işaret edebilir.

            4. Ani Hacim Patlamaları ve Momentum

                Yüksek Hacimle Ani Fiyat Hareketi: Hacimde ani bir artış, özellikle momentumda da keskin bir hareketle birlikte gerçekleşiyorsa, piyasanın yönünde hızlı bir değişim beklenebilir. Ani bir hacim patlamasıyla beraber momentumda büyük bir artış, trende ivme kazandırabilir.

            5. Momentum Taban Seviyelerindeyken Hacim Artışı

                Momentum göstergesi negatif seviyelerde (aşırı satım) seyrederken hacimde bir artış varsa, bu durum yatırımcıların ilgi göstermeye başladığını gösterebilir. Bu, fiyatların toparlanabileceği veya mevcut düşüş trendinin sona erebileceği anlamına gelebilir.

            6. Momentum ve Hacim Analizinin Birlikte Kullanımı

                Trend Gücünü Onaylama: Hacim, momentum göstergesi tarafından verilen sinyalleri doğrulamak için kullanılabilir. Momentum pozitif yönlü olduğunda hacmin de artması, trendin güçlü olduğunu gösterir ve bu yükseliş trendinin devam etme olasılığını artırır.
                Trend Değişim Sinyalleri: Hacim düşüşü, momentum göstergesi ile birleştiğinde, mevcut trendin zayıflayabileceğine veya tersine dönebileceğine dair bir sinyal olarak görülebilir.

            Özetle, hacim ve momentum birlikte analiz edildiğinde piyasanın mevcut trendinin gücü ve devam etme olasılığı hakkında daha net sinyaller verir. Momentum göstergesi, trendin hızını ve yönünü gösterirken, hacim bu trendin sürdürülebilirliğine dair ek bir doğrulama sağlar.
        """

    def de_marker(df,period=14):
        # Örneğin bir DataFrame'de 'high', 'low' ve 'close' sütunları mevcutsa
        
        isim = f"demarker_{period}"
        df[isim] = ta.momentum.DeMarkerIndicator(
            high=df['high'],
            low=df['low'],
            window=period  # Varsayılan olarak 14, ihtiyacınıza göre değiştirebilirsiniz
        ).dem()

        return df

    # volume_indicators = [func for func in dir(momentum) if callable(getattr(momentum, func)) and not func.startswith("_")]
    # pprint.pprint(volume_indicators)
    """
    ['AwesomeOscillatorIndicator',
    'IndicatorMixin',
    'KAMAIndicator',
    'PercentagePriceOscillator', 
    'PercentageVolumeOscillator',
    'ROCIndicator',
    'RSIIndicator',
    'StochRSIIndicator',
    'StochasticOscillator',      
    'TSIIndicator',
    'UltimateOscillator',        
    'WilliamsRIndicator',        
    'awesome_oscillator',        
    'kama',
    'ppo',
    'ppo_hist',
    'ppo_signal',
    'pvo',
    'pvo_hist',
    'pvo_signal',
    'roc',
    'rsi',
    'stoch',
    'stoch_signal',
    'stochrsi',
    'stochrsi_d',
    'stochrsi_k',
    'tsi',
    'ultimate_oscillator',
    'williams_r']
    """

    #   ----------      HACİM        -----------------
    def obv_ta(df):
        # OBV göstergesini oluştur
        obv = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume'])

        # OBV hesapla
        df['obv'] = obv.on_balance_volume()
        return df

    def vwap_haof_ta(df):
        # VWAP göstergesini oluştur      
        vwap = VolumeWeightedAveragePrice(high=df['high'], low=df['low'], close=df['close'], volume=df['volume'])

        # VWAP hesapla
        df['vwap'] = vwap.vwap
        return df

    def chaikin_money_flow_ta(df,period=20):
        
        isim_cmf = f"cmf_{period}"
        
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)


        # CMF göstergesini oluştur
        cmf = ChaikinMoneyFlowIndicator(high=df['high'], low=df['low'], close=df['close'], volume=df['volume'], window=period)

        # CMF hesapla ve sonucu DataFrame'e ekle
        df[isim_cmf] = cmf.chaikin_money_flow()
        return df

    # volume_indicators = [func for func in dir(volume) if callable(getattr(volume, func)) and not func.startswith("_")]
    # pprint.pprint(volume_indicators)

    """
    ['AccDistIndexIndicator',
    'ChaikinMoneyFlowIndicator',    
    'EaseOfMovementIndicator',         önemli bir indikatör.
    'ForceIndexIndicator',
    'IndicatorMixin',
    'MFIIndicator',
    'NegativeVolumeIndexIndicator', 
    'OnBalanceVolumeIndicator',     
    'VolumePriceTrendIndicator',    
    'VolumeWeightedAveragePrice',   
    'acc_dist_index',
    'chaikin_money_flow',
    'ease_of_movement',
    'force_index',
    'money_flow_index',
    'negative_volume_index',        
    'on_balance_volume',
    'sma_ease_of_movement',
    'volume_price_trend',
    'volume_weighted_average_price']
    """

    #  --------------    TREND   --------------------------

    def ema_ta(df, period=20):
        ema = EMAIndicator(close=df['close'], window=period)
        isim = f"ema_{period}" 
        
        df[isim] = ema.ema_indicator()
        
        return df

    def adx_di_ta(df,period=14):  # İNCELENECEK.
        # ADX ve MACD örneği
        isim_adx = f"adx_{period}"
        isim_pdi = f"pdi_{period}"
        isim_ndi = f"ndi_{period}"
        
        adx = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=period)

        df[isim_adx] = adx.adx()
        df[isim_pdi] = adx.adx_pos()
        df[isim_ndi] = adx.adx_neg()

        return df

    def sar_ta(df,step=0.02,max_step=0.2):   # Sorunsuz
        # SAR hesaplama (ta kütüphanesini kullanarak)
        sar_indicator = ta.trend.PSARIndicator(df['high'], df['low'], df['close'], step=step, max_step=max_step)
        df['SAR'] = sar_indicator.psar()
        isim_sar_long = f"sar_long_{step}_{max_step}"
        isim_sar_short = f"sar_short_{step}_{max_step}"
        # Long ve Short SAR değerlerini ayırmak
        df[isim_sar_long] = df['SAR'].where(df['SAR'] < df['close'], None)  # SAR değeri kapanış fiyatının altındaysa long
        df[isim_sar_short] = df['SAR'].where(df['SAR'] > df['close'], None)  # SAR değeri kapanış fiyatının üstündeyse short
        df = df.drop(columns=['SAR'])
        return df

    def macd_ta(df, slow_period=26, fast_period=12, signal_period=9):
        """
        MACD hesaplar ve DataFrame'e ekler.
        """
        
        isim_macd = f"macd_{slow_period}_{fast_period}_{signal_period}"
        isim_macd_signal = f"macd_signal_{slow_period}_{fast_period}_{signal_period}"
        isim_macd_hist = f"macd_hist_{slow_period}_{fast_period}_{signal_period}"
        
        macd = MACD(
            close=df['close'],
            window_slow=slow_period,
            window_fast=fast_period,
            window_sign=signal_period
        )
        df[isim_macd] = macd.macd()
        df[isim_macd_signal] = macd.macd_signal()
        df[isim_macd_hist] = macd.macd_diff()  # Direkt histogramı al
        
        return df

    def vidya(df, period=14, alpha=0.2):
        """
        yildizli_m kullanıcısı 14-0.002 ve 34-0.002 ohlc4 ayarlarıyla vidya kesişimlerinde güzel sonuçlar var. 
        """
        # VIDYA hesaplama
        isim_vidya = f"vidya_{period}_{alpha}"
        df[isim_vidya] = ta.trend.vidya(df['close'], window=period, alpha=alpha)
        
        return df

    # trend_indicators = [func for func in dir(trend) if callable(getattr(trend, func)) and not func.startswith("_")]
    # pprint.pprint(trend_indicators)
    """
    ['ADXIndicator',
    'AroonIndicator',   
    'CCIIndicator',     
    'DPOIndicator',     
    'EMAIndicator',     
    'IchimokuIndicator',
    'IndicatorMixin',   
    'KSTIndicator',     
    'MACD',
    'MassIndex',        
    'PSARIndicator',    
    'SMAIndicator',     
    'STCIndicator',     
    'TRIXIndicator',    
    'VortexIndicator',  
    'WMAIndicator',     
    'adx',
    'adx_neg',
    'adx_pos',
    'aroon_down',       
    'aroon_up',
    'cci',
    'dpo',
    'ema_indicator',
    'ichimoku_a',
    'ichimoku_b',
    'ichimoku_base_line',
    'ichimoku_conversion_line',
    'kst',
    'kst_sig',
    'macd',
    'macd_diff',
    'macd_signal',
    'mass_index',
    'psar_down',
    'psar_down_indicator',
    'psar_up',
    'psar_up_indicator',
    'sma_indicator',
    'stc',
    'trix',
    'vortex_indicator_neg',
    'vortex_indicator_pos',
    'wma_indicator']
    """

    #   ----------      VOLATİLİTE --- OYNAKLIK        -------------

    def bollinger(df, period=20, window_dev=3): # Sorunsuz
        # SMA ile Bollinger Bands hesaplama
        
        isim_ust= f"bol_std_ust_{period}_{window_dev}"
        isim_gercek_ust=f"bol_gercek_ust_{period}_{window_dev}"
        isim_orta= f"bol_std_orta_{period}_{window_dev}"
        isim_alt= f"bol_std_alt_{period}_{window_dev}"
        isim_gercek_alt=f"bol_gercek_alt_{period}_{window_dev}"
        isim_ust_sinyal= f"bol_std_ust_sinyal_{period}_{window_dev}"
        isim_alt_sinyal= f"bol_std_alt_sinyal_{period}_{window_dev}"
        
        bb_indicator = BollingerBands(close=df['close'], window=period, window_dev=window_dev)
        
        df[isim_ust] = bb_indicator.bollinger_hband()
        df[isim_gercek_ust]=bb_indicator.bollinger_hband()
        
        df[isim_orta] = bb_indicator.bollinger_mavg()
        
        df[isim_alt] = bb_indicator.bollinger_lband()
        df[isim_gercek_alt] = bb_indicator.bollinger_lband()
        
        df[isim_ust_sinyal] = bb_indicator.bollinger_hband_indicator()
        df[isim_alt_sinyal] = bb_indicator.bollinger_lband_indicator()
        
        # En son kapanış fiyatını al
        orjinal_kapanis =   df["close"].iloc[-1]  
        fiyat =             df["close"].iloc[-1]
        bol_alt = df[isim_gercek_alt].iloc[-1]
        
        while fiyat > bol_alt:
            fiyat = bol_alt  # Fiyatı Bollinger alt bandına eşitle
            df.loc[df.index[-1], "close"] = fiyat  # Güncellenmiş fiyatı DataFrame'e yaz
            
            # Bollinger bantlarını tekrar hesapla
            bb_indicator = BollingerBands(close=df['close'], window=period, window_dev=window_dev)
            df[isim_gercek_alt] = bb_indicator.bollinger_lband()
            bol_alt = df[isim_gercek_alt].iloc[-1]
        
        df.loc[df.index[-1], "close"]=orjinal_kapanis
        
        
        orjinal_kapanis =   df["close"].iloc[-1]  
        fiyat =             df["close"].iloc[-1]
        bol_ust = df[isim_gercek_ust].iloc[-1]
        
        while fiyat < bol_ust:
            fiyat = bol_ust  # Fiyatı Bollinger üst bandına eşitle
            df.loc[df.index[-1], "close"] = fiyat  # Güncellenmiş fiyatı DataFrame'e yaz
            
            # Bollinger bantlarını tekrar hesapla
            bb_indicator = BollingerBands(close=df['close'], window=period, window_dev=window_dev)
            df[isim_gercek_ust] = bb_indicator.bollinger_hband()
            bol_ust = df[isim_gercek_ust].iloc[-1]
            
        df.loc[df.index[-1], "close"]=orjinal_kapanis
        return df

    def atr_rma(df, period=14, carpan=1):
        """
        ATR hesaplaması için RMA (Smoothed Moving Average) yöntemi kullanan fonksiyon.
        
        Parametreler:
        df (DataFrame): Mum verilerini içeren pandas DataFrame (high, low, close kolonlarını içermelidir)
        period (int): ATR hesaplamasında kullanılan periyot uzunluğu (default 14)

        Dönüş:
        Pandas Series: ATR hesaplamalarının olduğu bir pandas serisi döner.
        """
        isim = f"atr_rma_{period}"
        
        # 'high', 'low', ve 'close' sütunlarını kullanarak ATR hesaplaması
        high = df['high']
        low = df['low']
        close = df['close']
        
        # ATR hesaplama
        atr = ta.volatility.average_true_range(high=high, low=low, close=close, window=period)
        atr = atr * carpan  # ATR değerini çarpan ile ölçekleme
        # RMA (Smoothed Moving Average) uygulayarak ATR hesaplama
        df[isim] = atr.ewm(alpha=1/period, adjust=False).mean()

        return df

    def ulcer_index(df, period=14):
        """
        Ulcer Index hesaplaması
        :param df: Pandas DataFrame, kapanış fiyatları içeren bir sütun 'close'
        :param period: Ulcer Index hesaplama periyodu (varsayılan 14)
        :return: Ulcer Index değerlerinin olduğu bir Pandas Series
        """
        
        isim= f"ulcer_index_{period}"
        # Yüksek fiyatın belirlenmesi
        rolling_max = df['close'].rolling(window=period, min_periods=1).max()
        
        # Geri çekilmenin hesaplanması (Drawdown)
        drawdown = (df['close'] - rolling_max) / rolling_max * 100
        
        # Geri çekilme karelerinin ortalaması
        ulcer_index = np.sqrt((drawdown ** 2).rolling(window=period, min_periods=1).mean())

        df[isim] = ulcer_index
        return df

    def donchian_channel(df, period=20):
        """
        Donchian Kanal hesaplaması
        :param df: Pandas DataFrame, en azından 'high' ve 'low' sütunları içermelidir
        :param period: Donchian Kanal periyodu (varsayılan 20)
        :return: Üst ve alt bantları içeren DataFrame sütunları
        """
        
        isim_ust = f"donchian_ust_{period}"
        isim_orta = f"donchian_orta_{period}"
        isim_alt = f"donchian_alt_{period}"
        # Üst Bant: Belirtilen dönem boyunca en yüksek fiyat
        df[isim_ust] = df['high'].rolling(window=period, min_periods=1).max()
        
        # Alt Bant: Belirtilen dönem boyunca en düşük fiyat
        df[isim_alt]= df['low'].rolling(window=period, min_periods=1).min()
        
        # Orta Bant: Üst ve Alt bantların ortalaması
        df[isim_orta] = (df['donchian_upper'] + df['donchian_lower']) / 2
        
        return df

    def choppiness_index(df, period=14):
        """
        Choppiness Index hesaplaması
        :param df: Pandas DataFrame, en az 'high' ve 'low' sütunlarını içermelidir
        :param period: Choppiness Index periyodu (varsayılan 14)
        :return: Choppiness Index değeri eklenmiş Pandas DataFrame
        """
        isim = f"choppiness_index_{period}"
        # Yüksek ve düşük fiyatlar üzerinden gerekli hesaplamalar
        high_max = df['high'].rolling(window=period, min_periods=1).max()
        low_min = df['low'].rolling(window=period, min_periods=1).min()
        tr_sum = (df['high'] - df['low']).rolling(window=period, min_periods=1).sum()
        
        # Choppiness Index hesaplaması
        df[isim] = 100 * np.log10(tr_sum / (high_max - low_min)) / np.log10(period)
        
        return df

    # volatility_indicators = [func for func in dir(volatility) if callable(getattr(volatility, func)) and not func.startswith("_")]
    # pprint.pprint(volatility_indicators)

    """
    ['AverageTrueRange',
    'BollingerBands',
    'DonchianChannel',
    'IndicatorMixin',
    'KeltnerChannel',
    'UlcerIndex',
    'average_true_range',
    'bollinger_hband',
    'bollinger_hband_indicator',      
    'bollinger_lband',
    'bollinger_lband_indicator',      
    'bollinger_mavg',
    'bollinger_pband',
    'bollinger_wband',
    'donchian_channel_hband',
    'donchian_channel_lband',
    'donchian_channel_mband',
    'donchian_channel_pband',
    'donchian_channel_wband',
    'keltner_channel_hband',
    'keltner_channel_hband_indicator',
    'keltner_channel_lband',
    'keltner_channel_lband_indicator',
    'keltner_channel_mband',
    'keltner_channel_pband',
    'keltner_channel_wband',
    'ulcer_index']
    
    
    Strateji Örneği
    # RSI ve UI birlikte karar verme
    
        if rsi < 30 and ulcer_index < 5:
            print("Al sinyali: Düşük risk ve RSI aşırı satım bölgesinde.")
        elif rsi > 70 and ulcer_index > 10:
            print("Sat sinyali: Yüksek risk ve RSI aşırı alım bölgesinde.")
    """


    """     --------------------------------------- TALİB KISMI ---------------------------------------------    """
    
    
    """     --------------------------------------- CUSTOM KISMI ---------------------------------------------    """
    def kapanis(df, n=0):
        n = (n * -1) - 1
        if abs(n) >= len(df):
            n=0
            n = (n * -1) - 1
        
        return df['close'].iloc[n]


    TA_INDICATORS = {
        # Momentum
        "RSI": rsi_ta,
        "CMO": cmo_ta,
        "STOKASTIK": stokastik,
        "WILLIAMS_R": williams_r,
        "AWESOME_OSCILLATOR_WITH_SIGNAL":awesome_oscillator_with_signal,
        "TSI":tsi,
        "ROC":roc,
        "PPO":ppo,
        "MOMENTUM":momentum_ta,
        "DE_MARKER":de_marker,
        # Hacim ve Volume
        "OBV":obv_ta,
        "VWAP":vwap_haof_ta,
        "CMF":chaikin_money_flow_ta,
        # Trend
        "EMA":ema_ta,
        "ADX_DI":adx_di_ta,
        "SAR":sar_ta,
        "MACD":macd_ta,
        "VIDYA":vidya,
        # Volatilite
        "BOLLINGER":bollinger,
        "ATR_RMA":atr_rma,
        "ULCER_INDEX":ulcer_index,
        "DONCHIAN_CHANNEL":donchian_channel,
        "CHOPPINESS_INDEX":choppiness_index,
    }
    TALIB_INDICATORS = {
  
    }

    CUSTOM_INDICATORS = {

        "KAPANIS": kapanis,
    }


    @staticmethod
    def get_indicator_function(indikator_obj):
        if not indikator_obj.aktif_mi:
            raise ValueError(f"{indikator_obj.adi} şu anda aktif değil.")
        return {
            'ta': IndikatorMotoru.TA_INDICATORS.get(indikator_obj.adi),
            'ta-lib': IndikatorMotoru.TALIB_INDICATORS.get(indikator_obj.adi),
            'custom': IndikatorMotoru.CUSTOM_INDICATORS.get(indikator_obj.adi),
        }.get(indikator_obj.kutuphane)

    @staticmethod
    def hesapla(indikator_obj, veriler, parametreler=None):
        if not indikator_obj.aktif_mi:
            raise ValueError(f"{indikator_obj.adi} şu anda aktif değil.")
        
        # Parametreleri birleştir
        params = {**indikator_obj.default_parametreler, **(parametreler or {})}
        
        # İndikatör fonksiyonunu seç
        indicator_function = IndikatorMotoru.get_indicator_function(indikator_obj)
        if not callable(indicator_function):
            raise ValueError(f"{indikator_obj.adi} desteklenmeyen bir indikatördür.")
        
        # İndikatör hesaplama
        return indicator_function(veriler, **params)

"""     --------------------------------------- YF GENEL FONKSİYONLARI ---------------------------------------------    """

#   Binance'mumlarını DF'e dönüştürür.
