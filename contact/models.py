from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from catalog.models import City

phone_regex = RegexValidator(
    regex=r'^\d{10,}$',
    message="El número debe contener al menos 10 dígitos numéricos."
)

class Contact(models.Model):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Este nombre de contacto ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Dirección",
        error_messages={
            'max_length': "La dirección no puede exceder 255 caracteres."
        }
    )
    email = models.CharField(
        max_length=100,
        unique=True,
        validators=[EmailValidator(message="Debe ser un correo electrónico válido")],
        verbose_name="Correo electrónico"
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Teléfono"
    )
    city_id = models.ForeignKey(
        City,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Ciudad"
    )

    class Meta:
        db_table = 'contact_contacts'
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"

    def __str__(self):
        return self.name
