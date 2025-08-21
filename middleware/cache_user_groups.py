from django.utils.deprecation import MiddlewareMixin
from django.apps import apps


class CacheUserGroupsMiddleware(MiddlewareMixin):
    """
    - user._group_names = set de nombres de grupo
    - user._workcell_ids  = lista de IDs de WorkCell para el user
    """

    def process_request(self, request):
        user = getattr(request, 'user', None)
        if not (user and user.is_authenticated):
            # asegurar que siempre exista
            if user:
                user._group_names = set()
                user._workcell_ids = []
            return

        # 1) Cachear grupos
        user._group_names = set(
            user.groups.values_list('name', flat=True)
        )

        # 2) Encontrar el modelo WorkCell
        WorkCell = apps.get_model('catalog', 'WorkCell')

        # 3) Tratar de usar el manager inverso correcto
        #    probamos varios posibles related_name
        possible_attrs = [
            'workcell_set',  # default si no hay related_name
            'work_cells',  # quizá related_name="work_cells"
            'workcell_users',  # o "workcell_users"
            'work_cells_users',  # o "work_cells_users"
        ]
        manager = None
        for attr in possible_attrs:
            if hasattr(user, attr):
                manager = getattr(user, attr)
                break

        if manager is None:
            # fallback directo
            qs = WorkCell.objects.filter(users=user)
        else:
            qs = manager.all()

        # 4) Finalmente, cacheamos los IDs
        user._workcell_ids = list(qs.values_list('id', flat=True))
