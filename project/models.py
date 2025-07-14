from django.db import models
from catalog.models import ProjectStatus, Specialty, Subdivision, BusinessGroup, WorkCell, BaseModel
from model_utils.models import SoftDeletableModel, TimeStampedModel

class Project(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Este nombre de proyecto ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción"
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
    # history = HistoricalRecords()

    project_status = models.ForeignKey(
        ProjectStatus,
        on_delete=models.DO_NOTHING,
        verbose_name="Estatus del proyecto"
    )
    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Especialidad"
    )
    subdivision = models.ForeignKey(
        Subdivision,
        on_delete=models.DO_NOTHING,
        verbose_name="Subdivisión"
    )

    work_cell = models.ForeignKey(
        WorkCell,
        on_delete=models.DO_NOTHING,
        verbose_name="Célula de trabajo"
    )

    class Meta:
        db_table = 'project_projects'
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"

    def __str__(self):
        return self.description or "Proyecto sin descripción"
