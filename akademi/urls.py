# akademi/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.akademi_index, name='akademi_index'),
    path('sozluk', views.sozluk, name='akademi_sozluk'),
]

