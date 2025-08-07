from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pariteler, Interval, MarketType, PariteIntervalMarket

@receiver(post_save, sender=Pariteler)
def create_pariteintervalmarket_for_pariteler(sender, instance, created, **kwargs):
    if created:
        intervals = Interval.objects.all()
        market_types = MarketType.objects.all()
        
        if instance.tip == "parite":
            for interval in intervals:
                for market in market_types:
                    PariteIntervalMarket.objects.get_or_create(
                        parite=instance, interval=interval, market=market
                    )
        elif instance.tip == "endeks":
            for interval in intervals:
                PariteIntervalMarket.objects.get_or_create(
                    parite=instance, interval=interval,
                    market=None  # Market boş olmalı
                )

@receiver(post_save, sender=Interval)
def create_pariteintervalmarket_for_interval(sender, instance, created, **kwargs):
    if created:
        pariteler = Pariteler.objects.all()
        market_types = MarketType.objects.all()

        for parite in pariteler:
            if parite.tip == "parite":
                for market in market_types:
                    PariteIntervalMarket.objects.get_or_create(
                        parite=parite, interval=instance, market=market
                    )
            elif parite.tip == "endeks":
                PariteIntervalMarket.objects.get_or_create(
                    parite=parite, interval=instance, market=None
                )

@receiver(post_save, sender=MarketType)
def create_pariteintervalmarket_for_markettype(sender, instance, created, **kwargs):
    if created:
        pariteler = Pariteler.objects.filter(tip="parite")  # Sadece normal pariteler için çalış
        intervals = Interval.objects.all()

        for parite in pariteler:
            for interval in intervals:
                PariteIntervalMarket.objects.get_or_create(
                    parite=parite, interval=interval, market=instance
                )
