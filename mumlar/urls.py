from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'mumlar'

urlpatterns = [
    path("", views.mumlar_index, name="mumlar_index"),
    path("pariteler_ve_interval",views.pariteler_ve_interval,name="pariteler_ve_interval"),
    path("parite_ekle",views.parite_ekle, name="parite_ekle")
]
