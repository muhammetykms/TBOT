# stratejiler/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import IslemAdimi

@receiver(post_save, sender=IslemAdimi)
def islem_adimi_eklenince_acik_islem_guncelle(sender, instance, created, **kwargs):
    if created and instance.islem_tipi == 'AL':
        instance.acik_islem.guncelle()
