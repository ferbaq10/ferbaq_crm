from django.contrib.auth import get_user_model
from users.models import RolePolicy, RoleScope

User = get_user_model()

SCOPE_WEIGHT = {
    RoleScope.NONE: 0,
    RoleScope.OWNED: 1,
    RoleScope.WORKCELL: 2,
    RoleScope.ALL: 3,
}

def resolve_scope(user: User) -> str:
    """
    Determina el alcance (scope) de acceso a datos para un usuario según las políticas de rol (RolePolicy).

    Lógica de funcionamiento:
    1. Si el usuario es superusuario (`is_superuser`), automáticamente recibe el alcance más alto (RoleScope.ALL).
    2. Se obtienen todos los IDs de grupos a los que pertenece el usuario.
    3. Se consultan las políticas de rol (RolePolicy) asociadas a esos grupos,
       ordenadas por prioridad ascendente y, en caso de empate, por ID.
       - Solo se seleccionan los campos necesarios: id, group_id, scope, priority.
    4. Si el usuario no tiene ninguna política asociada, se retorna RoleScope.NONE (sin acceso).
    5. Entre todas las políticas encontradas:
       - Se determina la prioridad más baja (número más pequeño).
       - Se filtran las políticas que tengan esa prioridad (puede haber varias con la misma).
    6. Si hay varias políticas con la misma prioridad, se elige la de mayor "peso" según `SCOPE_WEIGHT`:
       - ALL     → 3 (acceso más amplio)
       - WORKCELL → 2
       - OWNED   → 1
       - NONE    → 0
    7. Se retorna el `scope` seleccionado, que será usado para filtrar datos en otros métodos.

    Este método permite:
    - Resolver conflictos cuando un usuario pertenece a varios grupos con diferentes alcances.
    - Controlar el acceso modificando únicamente las políticas en la base de datos, sin tocar código.
    - Establecer un sistema de prioridades para definir qué alcance predomina.

    Parámetros:
        user (User): Usuario autenticado.

    Retorna:
        str: El alcance de acceso correspondiente (uno de los valores de RoleScope).
    """
    # Caso especial: el superusuario siempre tiene acceso total.
    if user.is_superuser:
        return RoleScope.ALL

    # Obtener IDs de grupos del usuario.
    group_ids = user.groups.values_list('id', flat=True)

    # Consultar políticas asociadas a esos grupos.
    policies = list(
        RolePolicy.objects
        .filter(group_id__in=group_ids)
        .order_by('priority', 'id')  # Prioridad más baja primero.
        .only('id', 'group_id', 'scope', 'priority')
    )

    # Si no hay políticas, no hay acceso.
    if not policies:
        return RoleScope.NONE

    # Determinar la prioridad más baja.
    min_priority = min(p.priority for p in policies)

    # Filtrar solo políticas con esa prioridad.
    candidates = [p for p in policies if p.priority == min_priority]

    # Entre las políticas con misma prioridad, elegir la de mayor "peso" (ALL > WORKCELL > OWNED > NONE).
    best = max(candidates, key=lambda p: SCOPE_WEIGHT[p.scope])

    # Retornar el alcance final.
    return best.scope
