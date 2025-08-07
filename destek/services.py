
import pandas as pd



def binance_mum_to_df(data, *columns):
    # print("binance_data_to")
    """
    Binance API'sinden gelen mum verilerini belirtilen sütunlarla bir DataFrame'e dönüştürür.
    Eğer sütunlar belirtilmezse, varsayılan olarak "open", "high", "low", "close" döndürülür.
    
    :param data: Binance API'den gelen mum verileri (liste içinde liste formatında)
    :param columns: Kullanıcının belirttiği sütunlar (değişken sayıda argüman)
    :return: Belirtilen veya varsayılan sütunları içeren bir DataFrame
    """
    # Binance verisinin tam sütun başlıklarını tanımla
    all_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                   'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
                   'taker_buy_quote_asset_volume', 'tarih']
    
    # Eğer sütun belirtilmemişse varsayılan sütunları kullan
    if not columns:
        columns = ('timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                   'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
                   'taker_buy_quote_asset_volume', 'tarih')  # Varsayılan sütunlar

    # Veriyi bir DataFrame'e dönüştür
    df = pd.DataFrame(data, columns=all_columns)
    
    # Belirtilen sütunların tiplerini kontrol ederek dönüştürme işlemi
    for col in columns:
        if col in df.columns:
            if col == 'timestamp':  # timestamp ve close_time için datetime dönüşümü yap
                df['tarih'] = df[col]
                df['tarih'] = pd.to_datetime(df['tarih'], unit='ms', utc=True)
                df['tarih'] = df['tarih'].dt.tz_convert('Europe/Istanbul')  # UTC+3 zaman dilimine çevir
            else:  # Diğer sütunları float'a çevir
                if col=='tarih':
                    pass
                else:
                    df[col] = df[col].astype(float)

    # Kullanıcının belirttiği veya varsayılan sütunları seç
    df = df[list(columns)]

    return df

