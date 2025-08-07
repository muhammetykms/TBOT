from django.shortcuts import render,get_object_or_404
from .models import Coinler  # Coinler modelini içe aktarın
# Create your views here.

def coinler_index(request):
    coinler_listesi=Coinler.objects.all()

    context={
        'coinler': coinler_listesi
    }

    return render(request, "coinler/coinler_index.html", context)


def coin_info(request, sembol):
    coin = get_object_or_404(Coinler, sembol__iexact=sembol)
    return render(request, 'coinler/coin_info.html', {'coin': coin})
