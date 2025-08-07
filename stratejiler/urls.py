from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'stratejiler'

urlpatterns = [
    path("", views.stratejiler_index, name="stratejiler_index"),

    path("strateji_icerigi_olustur/<int:strateji_id>", views.strateji_icerigi_olustur, name="strateji_icerigi_olustur"),
    # path("deneme/<int:strateji_id>", views.deneme, name="deneme"),
    
    path("strateji_kosulu_kaydet/", views.strateji_kosulu_kaydet, name="strateji_kosulu_kaydet"),
    path("strateji_detay/<int:strateji_id>/", views.strateji_detay, name="strateji_detay"),
    path('kosul_sil/', views.kosul_sil, name='kosul_sil'),
    path('kosul_bagla/', views.kosul_bagla, name='kosul_bagla'),
    path('strateji_sil/<int:strateji_id>', views.strateji_sil, name='strateji_sil'),
    
    
    # AJAXLAR
    path("ilk_secim_ajax/",views.ilk_secim_ajax,name="ilk_secim_ajax"),
    path("son_secim_ajax/",views.son_secim_ajax,name="son_secim_ajax"),
    
    path("yeni-kosul-formu/", views.yeni_kosul_formu, name="yeni_kosul_formu"),
    path("editor/", views.strateji_editor, name="strateji_editor"),
    path("market-select/", views.market_select, name="market_select"),
    path("coin-select/", views.coin_kumesi_select, name="coin_kumesi_select"),
    path('indikator_parametre_partial/', views.indikator_parametre_partial, name='indikator-parametre-partial'),
    path('karsilastirma-operatorleri/', views.karsilastirma_operatorleri_getir, name='karsilastirma_operatorleri'),
    path('if-blogu-ekle/', views.if_blogu_partial, name='if_blogu_ekle'),

    path('loop_blok_ekle/', views.loop_blok_ekle, name='loop_blok_ekle'),
    path('loop_adim_ekle/', views.loop_adim_ekle, name='loop_adim_ekle'),
    
    
    path("aksiyon_ekle/", views.aksiyon_ekle, name="aksiyon_ekle"),
    path('aksiyon_form/', views.aksiyon_form, name='aksiyon_form'),
    path('inside_buy_ekle/', views.inside_buy_ekle, name='inside_buy_ekle'),
    path('after_sell_ekle/', views.after_sell_ekle, name='after_sell_ekle'),
    path('data-save/',views.data_save, name='data_save'),
    
    # path('ve_grubu_ekle/', views.ve_grubu_ekle, name='ve_grubu_ekle'),
    path('veya_grubu_ekle/', views.veya_grubu_ekle, name='veya_grubu_ekle'),
    
    path('ic_ve_grubu_ekle/', views.ic_ve_grubu_ekle, name='ic_ve_grubu_ekle'),
    # path('ic_veya_grubu_ekle/', views.ic_veya_grubu_ekle, name='ic_veya_grubu_ekle'),
    
    path('state_ekle/', views.state_ekle, name='state_ekle'),
    path('if_state_kapanma_sarti/', views.if_state_kapanma_sarti, name='if_state_kapanma_sarti'),
    
    path('proses_ekle/', views.proses_ekle, name='proses_ekle'),
    
    path('test/', views.test_htmx_sayfasi, name='test_htmx'),

]
