from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'servisler'

urlpatterns = [
    path("", views.servisler_index, name="servisler_index"),
    path('check-service/', views.check_fastapi_service, name='check_fastapi_service'),
]

