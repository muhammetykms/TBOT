from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'coinler'

urlpatterns = [
    path("", views.coinler_index, name="coinler_index"),
    path('coin/<str:sembol>/', views.coin_info, name='coin_info'),

]


