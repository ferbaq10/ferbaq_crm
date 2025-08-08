from django.db import models
from simple_history.models import HistoricalRecords

from catalog.models import StatusOpportunity, City, Currency, BaseModel, OpportunityType, LostOpportunityType
from client.models import Client
from contact.models import Contact
from project.models import Project
from model_utils.models import SoftDeletableModel, TimeStampedModel
from django.conf import settings


class Opportunity(BaseModel):
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    closing_percentage = models.DecimalField(max_digits=4, blank=True, null=True,
                                             decimal_places=2, verbose_name="Porcentaje de cierre")
    amount = models.DecimalField(max_digits=12,
                                 decimal_places=2,
                                 blank=True, null=True,)
    requisition_number = models.CharField(max_length=100, verbose_name="Número de requisición",
                                          blank=True, null=True)
    date_reception = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de recepción")
    sent_date = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de enviado")
    date_status = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del estado")
    history = HistoricalRecords()

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
        blank=True,
        null=True,
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

    client = models.ForeignKey(
        Client,
        blank=True,
        null=True,
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
    earned_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto ganado")
    cost_subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Costo subtotal")
    order_closing_date = models.DateTimeField(blank=True, verbose_name="Fecha de cierre de orden")
    opportunity = models.OneToOneField(
        Opportunity,
        on_delete=models.DO_NOTHING,
        related_name = 'finance_data'
    )

    class Meta:
        db_table = 'opportunity_finance_opportunities'
        verbose_name = "Dato financiero de la oportunidad"
        verbose_name_plural = "Datos financieros de las oportunidades"

    def __str__(self):
        return f"Finanzas - {self.opportunity.name}"

class LostOpportunity(BaseModel):
    lost_opportunity_type = models.ForeignKey(
        LostOpportunityType,
        on_delete=models.DO_NOTHING,
        verbose_name="Tipo de oportunidad perdida"
    )
    opportunity = models.OneToOneField(
        Opportunity,
        on_delete=models.DO_NOTHING,
        related_name = 'lost_opportunity'
    )

class OpportunityDocument(models.Model):
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name="documents"
    )
    file_name = models.CharField(max_length=255)
    sharepoint_url = models.URLField(max_length=1000)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "opportunity_documents"
        verbose_name = "Documento de oportunidad"
        verbose_name_plural = "Documentos de oportunidad"

    def __str__(self):
        return self.file_name