# BU emri göndermeden önce marketin fiyatını kontrol eder.
# %5 den azmı çokmu gibi.


def market_take_bound_kontrol(mevcut_fiyat, teklif_fiyati, market_take_bound_orani):
    """
    Market order gönderilmeden önce fiyat sapmasını kontrol eder.
    
    :param mevcut_fiyat: Anlık en iyi fiyat (float)
    :param teklif_fiyati: Alım veya satımda gerçekleşecek fiyat (float)
    :param market_take_bound_orani: İzin verilen sapma yüzdesi (ör: 0.05 = %5)
    :return: True (uygun) veya False (sınır aşıldı)
    """
    max_izinli_fiyat = mevcut_fiyat * (1 + market_take_bound_orani)
    min_izinli_fiyat = mevcut_fiyat * (1 - market_take_bound_orani)

    if teklif_fiyati > max_izinli_fiyat or teklif_fiyati < min_izinli_fiyat:
        return False
    return True



# şimdi iptal edildiğiinde gibi bu gibi durumlarda bot ne yapacak ? kullanıcı bir strateji kurdu ve satış emri girdi marketten ama satış iptal edilince bot ne yapacak ?
