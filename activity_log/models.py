from django.db import models
from catalog.models import BaseModel, MeetingType, MeetingResult
from opportunity.models import Opportunity
from project.models import Project


class ActivityLog(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre"
    )
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

    project = models.ForeignKey(
        Project,
        on_delete=models.DO_NOTHING,
        verbose_name="Proyecto"
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