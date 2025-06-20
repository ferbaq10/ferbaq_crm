from django.db import models
from catalog.models import StatusOpportunity, City, Currency, BaseModel, OpportunityType
from contact.models import Contact
from project.models import Project
from model_utils.models import SoftDeletableModel, TimeStampedModel
from django.conf import settings


class Opportunity(BaseModel):
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    number_fvt = models.CharField(unique=True, max_length=100, verbose_name="Formato de venta")
    date_reception = models.DateTimeField(blank=True, verbose_name="Fecha de recepción")
    sent_date = models.DateTimeField(blank=True, verbose_name="Fecha de enviado")
    date_status = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del estado")
    status_opportunity = models.ForeignKey(
        StatusOpportunity,
        on_delete=models.DO_NOTHING
    )

    contact = models.ForeignKey(
        Contact,
        on_delete=models.DO_NOTHING
    )

    currency = models.ForeignKey(
        Currency,
        on_delete=models.DO_NOTHING
    )

    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        verbose_name="Usuario asignado"
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.DO_NOTHING
    )

    opportunityType = models.ForeignKey(
        OpportunityType,
        on_delete=models.DO_NOTHING
    )

    class Meta:
        db_table = 'opportunity_opportunities'
        verbose_name = "Oportunidad"
        verbose_name_plural = "Oportunidades"

    def __str__(self):
        return self.name

class CommercialActivity(BaseModel):
    name = models.CharField(unique=True, max_length=100)
    date_scheduled = models.DateTimeField(auto_now_add=True,
                                          verbose_name="Fecha programada")
    description = models.TextField(blank=True, null=True)

    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Usuario asignado"
    )

    opportunities = models.ManyToManyField(
        Opportunity,
        related_name='commercial_activities',
        verbose_name="Oportunidades asociadas",
        blank=True
    )

    class Meta:
        db_table = 'opportunity_commercial_activities'
        verbose_name = "Actividad comercial"
        verbose_name_plural = "Actividades comerciales"

    def __str__(self):
        return self.name

class FinanceOpportunity(BaseModel):
    name = models.CharField(unique=True, max_length=100)
    cost_subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    offer_subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    earned_amount = models.DecimalField(max_digits=12, decimal_places=2)
    order_closing_date = models.DateTimeField(blank=True, verbose_name="Fecha de cierre de orden")
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.DO_NOTHING
    )

    class Meta:
        db_table = 'opportunity_finance_opportunities'
        verbose_name = "Datos financieros de la oportunidad"
        verbose_name_plural = "Datos financieros de la oportunidades"

    def __str__(self):
        return self.name