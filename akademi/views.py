from django.shortcuts import render
from .models import Sozluk, SozlukDil
# Create your views here.
def akademi_index(request):
    return render(request, 'akademi/index.html')

from django.shortcuts import render
from .models import Sozluk, SozlukDil

def sozluk(request):
    dil = getattr(request, 'dil_tercihi', 'tr')
    ceviriler = SozlukDil.objects.select_related('sozluk').filter(dil=dil, onayli=True)

    veri_listesi = []
    for ceviri in ceviriler:
        veri_listesi.append({
            'terim': ceviri.sozluk.terim,
            'slug': ceviri.sozluk.terim.lower(),  # yönlendirme için kullanılabilir
            'baslik': ceviri.baslik
        })

    context = {
        'veriler': veri_listesi
    }
    return render(request, 'akademi/sozluk.html', context)


