from django.db import models


class Operatorler(models.Model):
    OPERATOR_GRUBU_CHOICES = [
        ('aritmatik', 'Aritmetik Operatörler'),
        ('karar', 'KARAR Operatörler'),
        ('karsilastirma', 'Karşılaştırma Operatörleri'),
        ('diger', 'Diğer Operatörler'),
    ]

    operator_adi = models.CharField(max_length=255)
    op_sembol = models.CharField(max_length=255)
    sembol=models.CharField(max_length=255,null=True,blank=True)
    op_grubu = models.CharField(
        max_length=50,
        choices=OPERATOR_GRUBU_CHOICES,
        default='ARITMETIK',
    )

    def __str__(self):
        return f"{self.operator_adi} ({self.op_sembol})"

