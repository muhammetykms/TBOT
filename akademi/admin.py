from django.contrib import admin
from .models import Sozluk, SozlukDil


@admin.register(Sozluk)
class SozlukAdmin(admin.ModelAdmin):
    list_display = ('terim', 'ekleyen', 'onayli', 'eklenme_tarihi')
    list_filter = ('onayli',)


@admin.register(SozlukDil)
class SozlukDilAdmin(admin.ModelAdmin):
    list_display = ('sozluk', 'kategori', 'dil', 'ekleyen', 'onayli', 'eklenme_tarihi')
    
    # Eğer kategori bazen boş olabiliyorsa 'SimpleListFilter' alternatifi değerlendirilebilir.
    list_filter = ('dil', 'onayli', 'kategori')  # Bu çalışmalı
