from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'destek'


urlpatterns = [
    path("", views.destek_index, name="destek_index"),

]
