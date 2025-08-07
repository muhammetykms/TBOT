def ortalama_alis_fiyati(n, ilk_fiyat=25.26, dusus_orani=0.12):
    toplam_usd = 0
    toplam_birim = 0
    onceki_toplam = 0

    print(" ")

    for i in range(n):
        fiyat = ilk_fiyat * (1 - dusus_orani * i)  # bu alımın gerçekleştiği coin fiyatı

        if i == 0:
            tutar = 100
        else:
            tutar = 2 * onceki_toplam

        birim = tutar / fiyat
        toplam_usd += tutar
        toplam_birim += birim
        onceki_toplam += tutar

        ort_fiyat = toplam_usd / toplam_birim
        yuzde_dusus = (1 - (ort_fiyat / ilk_fiyat)) * 100

        print(f"{i+1}. alım: {tutar:.2f} $ | koin fiyatı: {fiyat:.4f} | "
              f"ortalama: {ort_fiyat:.4f} | düşüş: %{yuzde_dusus:.4f}")

# Test
for n in range(1, 6):
    ortalama_alis_fiyati(n)
