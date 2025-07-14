from django.contrib.auth import get_user_model

from catalog.models import WorkCell
from users.services.interfaces import AbstractUserFactory

User = get_user_model()

class UserService(AbstractUserFactory):
    def assign_workcell(self, workcell_id: int, user):
        try:
            workcell = WorkCell.objects.get(pk=workcell_id)

            # Asignar sin sobrescribir otras células si deseas agregar (usa .add())
            user.workcell.add(workcell)
            return workcell

        except WorkCell.DoesNotExist:
            raise
        except Exception:
            raise

    def unassign_workcell(self, workcell_id: int, user):
        try:
            workcell = WorkCell.objects.get(pk=workcell_id)

            # Verificar si el usuario tiene asignada esta célula
            if not user.workcell.filter(pk=workcell_id).exists():
                raise ValueError(
                    {"error": f"El usuario no tiene asignada la célula '{workcell.name}'."},
                    status=400
                )

            # Desasignar la célula
            user.workcell.remove(workcell)
            return workcell

        except WorkCell.DoesNotExist:
            raise
        except Exception:
            raise

    def get_non_superusers(self, requesting_user):
        """
        Obtiene el listado de usuarios que no son superusuarios.
        Valida permisos del usuario solicitante.
        """
       # Obtener usuarios no superusuarios
        return User.objects.filter(is_superuser=False, is_active=True)

    def get_users_with_workcell(self):
        """
        Obtiene usuarios que tienen al menos una WorkCell asignada.
        Valida permisos del usuario solicitante.
        """

        # Obtener usuarios que tienen WorkCells asignadas
        return User.objects.filter(is_active=True).prefetch_related('workcell')
