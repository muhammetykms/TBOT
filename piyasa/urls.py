from django.urls import path
from . import views

urlpatterns = [
    path("", views.ozet_panel, name="ozet_panel"),
]
