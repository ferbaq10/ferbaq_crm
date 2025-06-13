from django.db import models
from catalog.models import StatusOpportunity, City, Currency
from contact.models import Contact
from model_utils.models import SoftDeletableModel, TimeStampedModel
from django.conf import settings


class CommercialActivity(SoftDeletableModel, TimeStampedModel):
    name = models.CharField(unique=True, max_length=100)
    date_scheduled = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Usuario asignado"
    )

    class Meta:
        db_table = 'opportunity_comercial_activities'
        verbose_name = "Actividad comercial"
        verbose_name_plural = "Actividades comerciales"

    def __str__(self):
        return self.name

class Opportunity(SoftDeletableModel, TimeStampedModel):
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    email = models.CharField(unique=True, max_length=100, blank=True, null=True)
    phone = models.IntegerField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status_opportunity = models.ForeignKey(
        StatusOpportunity,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True
    )

    city = models.ForeignKey(
        City,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True
    )

    currency = models.ForeignKey(
        Currency,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True
    )

    commercial_activity = models.ManyToManyField(
        CommercialActivity,
        blank=True,
        related_name='opportunities',
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Usuario asignado"
    )

    class Meta:
        db_table = 'opportunity_opportunities'
        verbose_name = "Oportunidad"
        verbose_name_plural = "Oportunidades"

    def __str__(self):
        return self.name