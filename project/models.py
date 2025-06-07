from django.db import models
from catalog.models import ProjectStatus, Speciality, Subdivision, BusinessGroup, WorkCell

class Project(models.Model):
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
    project_status = models.ForeignKey(
        ProjectStatus,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Estatus del proyecto"
    )
    speciality = models.ForeignKey(
        Speciality,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Especialidad"
    )
    subdivision = models.ForeignKey(
        Subdivision,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Subdivisión"
    )
    business_groups = models.ForeignKey(
        BusinessGroup,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Grupo empresarial"
    )
    work_cell = models.ForeignKey(
        WorkCell,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Célula de trabajo"
    )

    class Meta:
        db_table = 'project_projects'
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"

    def __str__(self):
        return self.description or "Proyecto sin descripción"
