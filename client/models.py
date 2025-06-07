from django.db import models
from catalog.models import City, BusinessGroup
from contact.models import Contact

class Client(models.Model):
    rfc = models.CharField(
        unique=True,
        max_length=20,
        verbose_name="RFC"
    )
    company = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Razón social"
    )
    city = models.ForeignKey(
        City,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Ciudad"
    )
    business_group = models.ManyToManyField(
        BusinessGroup,
        related_name='clients',
        blank=True,
        verbose_name="Grupo empresarial"
    )
    contact = models.ManyToManyField(
        Contact,
        related_name='clients',
        blank=True,
        verbose_name="Contactos"
    )

    class Meta:
        db_table = 'client_clients'
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.company

