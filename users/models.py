from django.db import models
from django.contrib.auth.models import Group, User

class RoleScope(models.TextChoices):
    OWNED = 'OWNED', 'Propias'
    WORKCELL = 'WORKCELL', 'Célula'
    ALL = 'ALL', 'Todas'
    NONE = 'NONE', 'Ninguna'

class RolePolicy(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        unique=True,               # un policy por grupo
        related_name='role_policy'
    )
    scope = models.CharField(
        max_length=20,
        choices=RoleScope.choices
    )
    priority = models.PositiveIntegerField(
        default=100,
        help_text='Menor número = mayor prioridad al resolver conflictos'
    )

    class Meta:
        ordering = ['priority', 'id']
        verbose_name = 'Política de Rol'
        verbose_name_plural = 'Políticas de Rol'

    def __str__(self):
        return f'{self.group.name} → {self.scope} (prio={self.priority})'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo_sharepoint_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL de la foto de perfil en SharePoint"
    )
    phone = models.CharField(max_length=15, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def get_photo_url(self):
        """Retorna la URL de la foto o None si no tiene"""
        return self.photo_sharepoint_url if self.photo_sharepoint_url else None
