from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models.signals import post_migrate
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Lista de modelos que quieres monitorear (los catálogos)
CATALOG_MODELS = [
    'Client',
]

APP_NAME = 'client'

def clear_list_cache_for(model_name):
    cache_key = f"{model_name}ViewSet_list"
    cache.delete(cache_key)
    print(f"Cache invalidado: {cache_key}")

# Registra dinámicamente las señales
def register_catalog_signals():
    for model_name in CATALOG_MODELS:
        model = apps.get_model(APP_NAME, model_name)

        def make_handler(model_name):
            def handler(sender, **kwargs):
                clear_list_cache_for(model_name)
            return handler

        handler = make_handler(model_name)

        post_save.connect(handler, sender=model, weak=False)
        post_delete.connect(handler, sender=model, weak=False)


@receiver(post_migrate)
def create_roles_and_permissions(sender, **kwargs):
    if sender.label != 'client':
        return

    model_names = ['Client']
    app_label = 'client'

    roles = {
        'Director Comercial': [],
        'Gerente Comercial': [],
        'Vendedor': [],
        'Comprador': [],
    }

    for role_name in roles:
        group, _ = Group.objects.get_or_create(name=role_name)
        roles[role_name] = group

    for model_name in model_names:
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model_name.lower())
        except ContentType.DoesNotExist:
            continue

        perms = Permission.objects.filter(content_type=ct)

        for perm in perms:
            roles['Director Comercial'].permissions.add(perm)

            if perm.codename.startswith(('view_', 'add_', 'change_')):
                roles['Gerente Comercial'].permissions.add(perm)

            if perm.codename.startswith('view_'):
                roles['Vendedor'].permissions.add(perm)
