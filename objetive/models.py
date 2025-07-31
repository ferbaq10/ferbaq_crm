from django.db import models
from catalog.models import Period, Currency, BaseModel
from django.conf import settings
from model_utils.models import SoftDeletableModel, TimeStampedModel

class Objetive(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Este nombre de objetivo ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Monto"
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True
    )

    period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Período"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Usuario asignado"
    )

    class Meta:
        db_table = 'objetive_objetives'
        verbose_name = "Objetivo"
        verbose_name_plural = "Objetivos"

    def __str__(self):
        return self.name
