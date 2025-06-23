from django.db import models
from catalog.models import BaseModel, MeetingType, MeetingResult
from opportunity.models import Opportunity, CommercialActivity
from project.models import Project
from contact.models import Contact

class ActivityLog(BaseModel):
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name="Latitud"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name="Longitud"
    )
    observation = models.TextField(
        blank=True,
        null=True,)

    activity_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de la actividad")

    activity_type = models.ForeignKey(
        CommercialActivity,
        on_delete=models.DO_NOTHING,
        verbose_name="Actividad comercial"
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.DO_NOTHING,
        verbose_name="Proyecto"
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.DO_NOTHING,
        verbose_name="Contacto"
    )
    meeting_type = models.ForeignKey(
        MeetingType,
        on_delete=models.DO_NOTHING,
        verbose_name="Tipo de reunión"
    )
    meeting_result = models.ForeignKey(
        MeetingResult,
        on_delete=models.DO_NOTHING,
        verbose_name="Resultado de la reunión"
    )

    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Oportunidad"
    )

    class Meta:
        db_table = 'activity_log_activity'
        verbose_name = "Registro de actividad"
        verbose_name_plural = "Registro de actividades"

    def __str__(self):
        return self.name