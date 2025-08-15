from django.db import models
from django.contrib.auth.models import Group

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
