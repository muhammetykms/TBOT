from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'islemac'

urlpatterns = [
    path("", views.islemac_index, name="islemac_index"),
]
