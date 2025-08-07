from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Modelinizdeki yeni alanları bu listeye ekleyin.
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('firma_kodu', 'full_name')}),
    )
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('firma_kodu', 'full_name')}),
    )
