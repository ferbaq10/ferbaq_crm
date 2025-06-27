from django.apps import apps
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete

# Lista de modelos que quieres monitorear (los catálogos)
CATALOG_MODELS = [
    'Project',
]

APP_NAME = 'project'

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
