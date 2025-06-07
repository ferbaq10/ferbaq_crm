from django.db import models
from catalog.models import StatusOpportunity, City
from contact.models import Contact

class Opportunity(models.Model):
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

    class Meta:
        db_table = 'opportunity_opportunities'
        verbose_name = "Oportunidad"
        verbose_name_plural = "Oportunidades"

    def __str__(self):
        return self.name
    

class ComercialActivity(models.Model):
    name = models.CharField(unique=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    oportunity_id = models.ForeignKey(
        Opportunity,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'opportunity_comercial_activities'
        verbose_name = "Actividad comercial"
        verbose_name_plural = "Actividades comerciales"

    def __str__(self):
        return self.name