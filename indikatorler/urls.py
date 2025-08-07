from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'indikatorler'

urlpatterns = [
    path("", views.indikatorler_index, name="indikatorler_index"),
    path('ind/', views.indikatör_gorunum, name='ind'),
    path('grafik/', views.grafik_gorunum, name='grafik'),
    path('indikator_guncelle/<int:id>', views.indikator_guncelle, name='indikator_guncelle'),
]
